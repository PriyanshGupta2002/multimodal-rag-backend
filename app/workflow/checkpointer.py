from contextlib import contextmanager

from psycopg import connect
from langgraph.checkpoint.postgres import PostgresSaver


@contextmanager
def create_checkpointer(database_url: str):
    conn_string = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    with connect(conn_string, autocommit=True) as conn:
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        yield checkpointer
