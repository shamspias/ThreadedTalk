from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Import your base metadata
from app.db.base import Base
from app.core.config import settings

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set your metadata here
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    # Provide the URL for 'offline' migrations:
    url = settings.SYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Create sync engine from SYNC_DATABASE_URL
    connectable = create_engine(settings.SYNC_DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
