# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/alembic/versions/0348ee946444_create_documents_table.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-19 09:03:39 UTC (1792400619)

"""create documents table\n\nRevision ID: 0348ee946444\nRevises: 2d709782c89f\nCreate Date: 2026-10-19 14:33:39.063132\n\n"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = '0348ee946444'
down_revision: Union[str, Sequence[str], None] = '2d709782c89f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Upgrade schema."""
    # ***<module>.upgrade: Failure: Different bytecode
    op.create_table('documents', sa.Column('id', sa.Uuid(), nullable=False), sa.Column('user_id', sa.Uuid(), nullable=False), sa.Column('filename', sa.String(length=255), nullable=False), sa.Column('file_url', sa.String(length=2048), nullable=False), sa.Column('imagekit_file_id', sa.String(length=50), server_default=sa.text('now()'), nullable=False), sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_documents_user_id_users'), ondelete='CASCADE'), sa.PrimaryKeyConstraint('id', name=op.f('pk_documents')), sa.UniqueConstraint('imagekit_file_id', name=op.f('uq_documents_imagekit_file_id')))
    op.create_index(op.f('ix_documents_status'), 'documents', ['status'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_status'), table_name='documents')
    op.drop_table('documents')