"""
Add face_templates table for Rolling Template System

Revision ID: add_face_templates
Revises: create_face_embeddings
Create Date: 2025-08-20 21:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = 'add_face_templates'
down_revision = 'create_face_embeddings'
branch_labels = None
depends_on = None

def upgrade():
    """Create face_templates table for rolling template system"""
    
    # Create face_templates table
    op.create_table(
        'face_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.String(50), nullable=False, index=True),
        sa.Column('image_id', sa.String(255), nullable=False, unique=True),
        sa.Column('embedding_vector', postgresql.ARRAY(sa.Float), nullable=False),
        sa.Column('template_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('created_from', sa.String(20), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('match_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_matched', sa.DateTime(), nullable=True),
        sa.Column('avg_match_confidence', sa.Float(), nullable=True),
        
        # Constraints
        sa.CheckConstraint('template_order >= 1 AND template_order <= 3', name='check_template_order'),
        sa.CheckConstraint("created_from IN ('ADMIN_UPLOAD', 'ATTENDANCE')", name='check_created_from'),
        sa.CheckConstraint('quality_score >= 0 AND quality_score <= 1', name='check_quality_score'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score'),
        sa.CheckConstraint('match_count >= 0', name='check_match_count'),
        sa.CheckConstraint('avg_match_confidence >= 0 AND avg_match_confidence <= 1', name='check_avg_confidence'),
        
        # Foreign key to employees table
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ondelete='CASCADE'),
        
        # Unique constraint: max 3 templates per employee
        sa.UniqueConstraint('employee_id', 'template_order', name='unique_employee_template_order')
    )
    
    # Create indexes for better performance
    op.create_index('idx_face_templates_employee_id', 'face_templates', ['employee_id'])
    op.create_index('idx_face_templates_created_at', 'face_templates', ['created_at'])
    op.create_index('idx_face_templates_last_matched', 'face_templates', ['last_matched'])
    op.create_index('idx_face_templates_quality', 'face_templates', ['quality_score'])
    
    # Create composite index for efficient template lookups
    op.create_index('idx_face_templates_employee_order', 'face_templates', ['employee_id', 'template_order'])

def downgrade():
    """Drop face_templates table and related indexes"""
    
    # Drop indexes first
    op.drop_index('idx_face_templates_employee_order')
    op.drop_index('idx_face_templates_quality')
    op.drop_index('idx_face_templates_last_matched')
    op.drop_index('idx_face_templates_created_at')
    op.drop_index('idx_face_templates_employee_id')
    
    # Drop table
    op.drop_table('face_templates')
