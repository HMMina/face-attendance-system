# 💾 Database Migration for Face Embeddings

"""create face_embeddings table

Revision ID: create_face_embeddings
Revises: [previous_revision]
Create Date: 2025-08-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'create_face_embeddings'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None

def upgrade():
    # Create face_embeddings table
    op.create_table(
        'face_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('embedding_vector', postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column('face_photo_path', sa.String(), nullable=True),
        sa.Column('confidence_threshold', sa.Float(), nullable=True, default=0.7),
        sa.Column('photo_quality', sa.Float(), nullable=True, default=0.0),
        sa.Column('registered_by', sa.String(), nullable=True, default='system'),
        sa.Column('registration_device', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_face_embeddings_id'), 'face_embeddings', ['id'], unique=False)
    op.create_index(op.f('ix_face_embeddings_employee_id'), 'face_embeddings', ['employee_id'], unique=False)
    op.create_index(op.f('ix_face_embeddings_is_active'), 'face_embeddings', ['is_active'], unique=False)
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_face_embeddings_employee_id', 
        'face_embeddings', 
        'employees',
        ['employee_id'], 
        ['employee_id']
    )
    
    # Install pgvector extension for vector similarity search (if using PostgreSQL)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create vector similarity index (requires pgvector extension)
    # Note: This might need to be done manually depending on your PostgreSQL setup
    # op.execute('CREATE INDEX face_embedding_vector_idx ON face_embeddings USING ivfflat (embedding_vector vector_cosine_ops)')

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_face_embeddings_is_active'), table_name='face_embeddings')
    op.drop_index(op.f('ix_face_embeddings_employee_id'), table_name='face_embeddings')
    op.drop_index(op.f('ix_face_embeddings_id'), table_name='face_embeddings')
    
    # Drop foreign key
    op.drop_constraint('fk_face_embeddings_employee_id', 'face_embeddings', type_='foreignkey')
    
    # Drop table
    op.drop_table('face_embeddings')
