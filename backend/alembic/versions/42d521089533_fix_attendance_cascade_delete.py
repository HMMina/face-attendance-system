"""fix_attendance_cascade_delete

Revision ID: 42d521089533
Revises: 5447c6b7b32c
Create Date: 2025-08-23 20:46:37.520490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42d521089533'
down_revision = '5447c6b7b32c'
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing foreign key constraint
    op.drop_constraint('attendance_employee_id_fkey', 'attendance', type_='foreignkey')
    
    # Recreate foreign key with CASCADE DELETE
    op.create_foreign_key(
        'attendance_employee_id_fkey', 
        'attendance', 
        'employees', 
        ['employee_id'], 
        ['employee_id'], 
        ondelete='CASCADE'
    )

def downgrade():
    # Drop CASCADE foreign key
    op.drop_constraint('attendance_employee_id_fkey', 'attendance', type_='foreignkey')
    
    # Recreate original foreign key without CASCADE
    op.create_foreign_key(
        'attendance_employee_id_fkey', 
        'attendance', 
        'employees', 
        ['employee_id'], 
        ['employee_id']
    )