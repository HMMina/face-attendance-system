"""recreate_face_templates_v2

Revision ID: 5447c6b7b32c
Revises: add_face_templates
Create Date: 2025-08-23 20:36:33.645355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5447c6b7b32c'
down_revision = 'add_face_templates'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the face_templates table completely and recreate with new structure
    op.drop_table('face_templates')
    
    # Create new face_templates table with enhanced structure
    op.create_table('face_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False, default=0),
        sa.Column('filename', sa.String(200), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('embedding_vector', sa.ARRAY(sa.Float()), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_from', sa.String(50), nullable=True),
        sa.Column('quality_score', sa.Float(), default=0.0),
        sa.Column('confidence_score', sa.Float(), default=0.0),
        sa.Column('match_count', sa.Integer(), default=0),
        sa.Column('last_matched', sa.DateTime(), nullable=True),
        sa.Column('avg_match_confidence', sa.Float(), default=0.0),
        
        # Add foreign key
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ondelete='CASCADE'),
        
        # Add constraints
        sa.UniqueConstraint('employee_id', 'image_id', name='unique_employee_image_id'),
        sa.CheckConstraint('image_id >= 0 AND image_id <= 3', name='image_id_check'),
        
        # Primary key
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop new table and recreate old structure
    op.drop_table('face_templates')
    
    # Recreate old face_templates table structure
    op.create_table('face_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.String(100), nullable=False),
        sa.Column('template_data', sa.LargeBinary(), nullable=False),
        sa.Column('template_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        
        # Foreign key
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        
        # Constraints
        sa.UniqueConstraint('image_id', name='face_templates_image_id_key'),
        sa.UniqueConstraint('employee_id', 'template_order', name='unique_employee_template'),
        sa.CheckConstraint('template_order > 0', name='template_order_check'),
        
        # Primary key
        sa.PrimaryKeyConstraint('id')
    )