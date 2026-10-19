# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/app/shared/db.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-18 12:17:44 UTC (1792325864)

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, MetaData
from app.shared.config import settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))
engine = create_engine(settings.DATABASE_URL)
LocalSession = sessionmaker(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
