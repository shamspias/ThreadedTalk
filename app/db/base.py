from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic's autogenerate support:
from app.models import conversation  # noqa
