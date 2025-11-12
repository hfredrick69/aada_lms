from logging.config import fileConfig
import os
import sys
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
sys.path.append(os.path.join(os.path.dirname(__file__), '...'))

load_dotenv()

config = context.config

# Don't use config.set_main_option() as it uses ConfigParser which treats % as interpolation
# Instead, get DATABASE_URL directly and use it when creating the engine
DATABASE_URL = os.getenv("DATABASE_URL")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


from app.db.base import Base  # noqa
from app.db.models import user, program, enrollment, xapi, scorm  # noqa
from app.db.models.compliance import attendance, skills, extern, finance, withdraw_refund, complaint, credential, transcript, audit  # noqa
from app.db.models.crm import lead, activity  # noqa

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Create engine directly from DATABASE_URL to avoid ConfigParser interpolation issues
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
