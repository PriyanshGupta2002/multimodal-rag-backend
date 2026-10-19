# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: '/Users/priyansh/Projects/multimodal-rag/backend/alembic/versions/2d709782c89f_create_users_table.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 2026-10-18 12:41:19 UTC (1792327279)

"""create users table\n\nRevision ID: 2d709782c89f\nRevises: \nCreate Date: 2026-10-18 18:11:19.628105\n\n"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = '2d709782c89f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Upgrade schema."""
    # ***<module>.upgrade: Failure: Different bytecode
    op.create_table('users', sa.Column('id', sa.Uuid(), nullable=False), sa.Column('name', sa.String(length=100), nullable=False), sa.Column('email', sa.String(length=255), nullable=False), sa.PrimaryKeyConstraint('id', name=op.f('pk_users')), sa.UniqueConstraint('email', name=op.f('uq_users_email')))
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')