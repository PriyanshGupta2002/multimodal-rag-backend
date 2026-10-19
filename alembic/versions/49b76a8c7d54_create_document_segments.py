# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/alembic/versions/49b76a8c7d54_create_document_segments.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 12:38:54 UTC (1792413534)

"""create document segments\n\nRevision ID: 49b76a8c7d54\nRevises: 0348ee946444\nCreate Date: 2026-10-19 18:07:13.901713\n\n"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import VECTOR
revision: str = '49b76a8c7d54'
down_revision: Union[str, Sequence[str], None] = '0348ee946444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Upgrade schema."""
    # ***<module>.upgrade: Failure: Different bytecode
    op.create_table('document_segments', sa.Column('id', sa.Uuid(), nullable=False), sa.Column('document_id', sa.Uuid(), nullable=False), sa.Column('page', sa.Integer(), nullable=False), sa.Column('modality', sa.String(length=20), nullable=False), sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False), sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name=op.f('fk_document_segments_document_id_documents'), ondelete='CASCADE'), sa.PrimaryKeyConstraint('id', name=op.f('pk_document_segments')))
    op.create_index(op.f('ix_document_segments_document_id'), 'document_segments', ['document_id'], unique=False)
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_document_segments_document_id'), table_name='document_segments')
    op.drop_table('document_segments')