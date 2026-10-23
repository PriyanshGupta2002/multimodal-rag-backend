# Multimodal RAG Backend

A Python API for document-grounded chat. Users can create conversations, upload documents, and ask questions answered from retrieved document content with citations. The backend combines FastAPI, PostgreSQL with pgvector, a background Celery worker, ImageKit file storage, Hugging Face sentence embeddings, and a LangGraph retrieval-and-generation workflow.

## Contents

- [What the application does](#what-the-application-does)
- [Architecture](#architecture)
- [Document ingestion and chat flows](#document-ingestion-and-chat-flows)
- [Technology choices](#technology-choices)
- [Project layout](#project-layout)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Run locally](#run-locally)
- [HTTP API](#http-api)
- [Data model](#data-model)
- [Current behavior and limitations](#current-behavior-and-limitations)

## What the application does

- Registers users and authenticates them with short-lived access and refresh JWTs stored in HTTP-only cookies.
- Stores user documents in ImageKit and tracks document metadata and processing status in PostgreSQL.
- Extracts PDF text, tables, and embedded images. Image content is summarized by a vision-language model so it can be searched alongside text.
- Embeds extracted content and retrieves relevant segments using PostgreSQL vector similarity.
- Streams answers from a RAG workflow as Server-Sent Events (SSE), with citations linked to retrieved segments.
- Stores chat threads and messages in PostgreSQL and persists LangGraph workflow checkpoints there as well.

## Architecture

```mermaid
flowchart LR
    Client[Web client] -->|HTTP, cookie auth, SSE| API[FastAPI application]
    API --> DB[(PostgreSQL<br/>SQLAlchemy + pgvector)]
    API -->|enqueue document task| Redis[(Redis)]
    Redis --> Worker[Celery worker]
    Worker -->|read and update metadata| DB
    Worker -->|upload originals and extracted images| Storage[ImageKit]
    Worker -->|PDF extraction and image summaries| Extract[PyMuPDF + vision model]
    Worker -->|create embeddings| Embeddings[Sentence Transformers]
    Extract --> DB
    Embeddings --> DB
    API -->|LangGraph retrieve and generate| RAG[RAG workflow]
    RAG -->|similarity search| DB
    RAG -->|LLM requests| Models[OpenRouter chat models]
    RAG -->|stream events| Client
    API -->|workflow checkpoints| DB
```

The API and worker share the same application settings and database models. The API handles synchronous requests and dispatches document processing; the Celery worker performs the longer-running extraction and embedding work. Chat retrieval and generation run through a compiled LangGraph workflow created during FastAPI startup. PostgreSQL stores application records, vector embeddings, and workflow checkpoints.

### Request boundaries

- Authentication is enforced for document, thread, and chat operations through the `access_token` cookie.
- Database access is provided through SQLAlchemy sessions.
- File bytes and derived image files live in ImageKit; PostgreSQL stores their URLs, ImageKit identifiers, and document metadata.
- Redis is the Celery broker and result backend.
- The chat endpoint streams named SSE events instead of returning one completed JSON response.

## Document ingestion and chat flows

### Document upload and indexing

1. An authenticated client sends a multipart upload to `POST /documents/upload`.
2. The API validates the content type, file signature, and 20 MB size limit, uploads the original file to ImageKit, and creates a document record with status `uploaded`.
3. The API queues `documents.process_document` in Celery and returns the document ID and file URL.
4. The worker downloads the document from ImageKit. For PDFs, it extracts page text and detected tables. It also extracts embedded images, uploads them to ImageKit, and requests concise factual image summaries from the vision model.
5. Text, table representations, and image summaries are embedded with `sentence-transformers/all-MiniLM-L6-v2` and stored as `document_segments` with metadata and page/modality information.
6. The document status is updated to `processed`; failures are recorded as `failed` with an error message when possible.

### Question answering

1. An authenticated client sends `POST /chat/stream` with a thread ID, message, and optional document ID.
2. The API verifies that the thread belongs to the user and saves the user message.
3. The LangGraph `retrieve` node embeds the query and searches the user's document segments by cosine distance. If a document ID was supplied, the search is limited to that document.
4. The `generate` node sends the retrieved context and question to the configured chat model. The prompt instructs the model to answer from context only and cite supporting sources.
5. The API streams generated text as `token` events, saves the completed assistant message with citations and usage metadata, and emits final citation and completion events.

The document-only search route uses the same embedding and retrieval logic and returns a generated answer with citations.

## Technology choices

| Area | Implementation |
| --- | --- |
| HTTP API | FastAPI, Pydantic |
| Persistence and migrations | SQLAlchemy, PostgreSQL, Alembic |
| Vector storage and similarity | pgvector (`Vector(384)`, cosine distance) |
| Background processing | Celery with Redis broker/backend |
| RAG orchestration and durable state | LangGraph with PostgreSQL checkpointer |
| PDF extraction | PyMuPDF |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` via Sentence Transformers / Hugging Face |
| Chat and image understanding | OpenRouter chat models |
| Original and extracted-image storage | ImageKit |
| Authentication | JWT, Argon2 password hashing, HTTP-only cookies |

The configured model IDs in the current document service are `qwen/qwen3.8-27b` for image summaries and `anthropic/claude-haiku-5.5` for text generation.

## Project layout

```text
app/
  auth/          Registration, login, token refresh, logout, and current-user endpoints
  chat/          Streaming chat API and chat orchestration service
  documents/     Upload/search APIs, extraction/indexing service, Celery task, and models
  messages/      Persisted chat-message model and service
  threads/       Conversation-thread API, service, and model
  user/          User model
  shared/        Settings, database session, authentication dependencies, and Celery app
  workflow/      LangGraph state, nodes, prompts, graph, and PostgreSQL checkpointer
alembic/
  versions/      Database schema migrations
  env.py         Alembic configuration using application settings and SQLAlchemy models
pyproject.toml   Package metadata and runtime dependencies
uv.lock          Locked dependency versions
alembic.ini      Alembic migration configuration
```

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- PostgreSQL with the pgvector extension available
- Redis
- ImageKit credentials
- An OpenRouter API key

PostgreSQL and Redis are external services; this repository does not currently include a Docker Compose configuration.

## Configuration

Create a `.env` file in the repository root. Do not commit real credentials.

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/multimodal_rag
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your-imagekit-id

REDIS_URL=redis://localhost:6379/0
OPENROUTER_API_KEY=your-openrouter-api-key
```

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy and LangGraph PostgreSQL connection. Use the `postgresql+psycopg://` scheme. |
| `SECRET_KEY` | Signs and verifies JWTs; use a strong, private value. |
| `ALGORITHM` | JWT signing algorithm, for example `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime and cookie max age. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token cookie max age. |
| `IMAGEKIT_PRIVATE_KEY` | Used by the backend to upload and delete files in ImageKit. |
| `IMAGEKIT_PUBLIC_KEY`, `IMAGEKIT_URL_ENDPOINT` | Required application settings for ImageKit configuration. |
| `REDIS_URL` | Celery broker and result-backend URL. |
| `OPENROUTER_API_KEY` | Used by the LangChain OpenRouter integration for model requests. |

The application loads its settings from environment variables and `.env`. The OpenRouter integration also expects its API key in the environment. Use separate credentials and a suitably protected secret key in each environment.

## Run locally

Run commands from the repository root.

1. Install Python dependencies:

   ```bash
   uv sync
   ```

2. Create the PostgreSQL database and ensure pgvector is installed and available. Configure `.env` as above.

3. Apply schema migrations:

   ```bash
   uv run alembic upgrade head
   ```

4. Start Redis and run the Celery worker in one terminal:

   ```bash
   uv run celery -A app.shared.celery_app:celery_app worker --loglevel=info
   ```

5. Run the API in another terminal:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

The API is served at `http://127.0.0.1:8000`. FastAPI's interactive documentation is available at `/docs`, and its OpenAPI schema at `/openapi.json`. CORS is currently configured for `http://localhost:3000` and `http://127.0.0.1:3000`.

Login cookies are marked `Secure` and `HttpOnly`; use HTTPS in environments where the browser requires secure cookies. The application currently does not define a separate health-check route.

## HTTP API

All routes are mounted without a version prefix. Document, thread, and chat routes, plus `GET /auth/me`, require the authenticated user's `access_token` cookie. Registration and login are public; token refresh and logout operate on the authentication cookies.

### Authentication

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a user. |
| `POST` | `/auth/login` | Authenticate and set access/refresh cookies. |
| `POST` | `/auth/refresh` | Use the refresh cookie to issue a new access cookie. |
| `POST` | `/auth/logout` | Clear the authentication cookies. |
| `GET` | `/auth/me` | Return the authenticated user's profile. |

### Documents

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/documents/upload` | Upload one multipart file and queue processing. |
| `GET` | `/documents` | List the current user's documents. |
| `GET` | `/documents/status/{doc_id}` | Get processing status for an owned document. |
| `POST` | `/documents/search-in-docs` | Search within the required `doc_id` using a JSON body with `query`; return a grounded answer and citations. |
| `DELETE` | `/documents/delete/{doc_id}` | Delete the owned document, its segments, and its original ImageKit file. |

An upload uses the multipart field `file`. The upload response includes `document_id`, `file_name`, and `file_url`. Processing is asynchronous; poll the status route until the status becomes `processed` or `failed`.

### Threads and chat

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/threads/create` | Create a thread with a title. |
| `GET` | `/threads` | List the user's threads. Supports `limit` (1–100, default 20) and `offset` (default 0). |
| `GET` | `/threads/{thread_id}` | Get an owned thread. |
| `PATCH` | `/threads/{thread_id}` | Update an owned thread's title. |
| `DELETE` | `/threads/{thread_id}` | Delete an owned thread and its messages. |
| `POST` | `/chat/stream` | Stream an answer for a thread. |
| `GET` | `/chat/{thread_id}/messages` | Fetch messages for an owned thread. |

`POST /chat/stream` accepts JSON shaped like:

```json
{
  "thread_id": "00000000-0000-0000-0000-000000000000",
  "message": "What does the report say about annual revenue?",
  "document_id": null
}
```

`document_id` is optional; when provided, retrieval is scoped to that document. The response is `text/event-stream` and uses these named events:

| Event | Payload |
| --- | --- |
| `start` | The active thread ID. |
| `token` | A text fragment in `content`. |
| `citations` | Final citation items. |
| `done` | Thread ID, whether the answer was saved, and token usage. |
| `error` | An error message if the request or workflow fails. |

## Data model

- **Users** own documents and threads. Passwords are stored as password hashes.
- **Documents** store owner, filename, file URL, ImageKit file ID, media type, size, status, and any processing error.
- **Document segments** store extracted text, tables, or image summaries with page number, modality, JSON metadata, and a normalized 384-dimensional embedding.
- **Threads** belong to users and contain ordered **messages**. Assistant message metadata stores citations and model usage.
- **LangGraph checkpoints** persist workflow state in PostgreSQL, separate from the application message history.

Schema changes are managed by Alembic. The migrations create the user, document, document-segment, thread, and message tables.

## Current behavior and limitations

- The upload validator accepts JPEG, PNG, and PDF files, but the asynchronous processor currently indexes PDFs only. Uploaded JPEG or PNG files will be marked `failed` with an explanatory status error.
- PDF extraction creates segments at page/content-type level; it is not a general-purpose document chunking pipeline.
- Image understanding is performed on images embedded in PDFs. The image is uploaded to ImageKit and its generated textual summary is indexed.
- Retrieval returns up to five nearest segments, scoped to the authenticated user and optionally one document. The direct document search route also uses the shared retrieval service.
- The application expects PostgreSQL/pgvector, Redis, ImageKit, and OpenRouter to be configured and reachable; local development does not provide substitutes for these external services.
- CORS origins and chat model identifiers are currently configured in application code.
