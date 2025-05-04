from alembic import op
import sqlalchemy as sa

# Добавление поля user_id в таблицу pet_profiles
def upgrade():
    op.add_column('pet_profiles', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_pet_profiles_user_id_users', 'pet_profiles', 'forum_user', ['user_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_pet_profiles_user_id_users', 'pet_profiles', type_='foreignkey')
    op.drop_column('pet_profiles', 'user_id')
