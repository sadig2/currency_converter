import asyncio
from contextlib import ExitStack

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from src.core.models import db_helper
from src.core.config import settings
from src.core.models import Base
from src.core.models.db_helper import get_db_session
from src.core.models import db_helper as sessionmanager
from src.main import main_app as actual_app
from asyncpg import Connection
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield actual_app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


def run_migrations(connection: Connection):
    config = Config("app/alembic.ini")
    config.set_main_option("script_location", "src/alembic")
    config.set_main_option("sqlalchemy.url", str(settings.db.url))
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    context = MigrationContext.configure(
        connection, opts={"target_metadata": Base.metadata, "fn": upgrade}
    )

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Run alembic migrations on test DB
    async with sessionmanager.connect() as connection:
        await connection.run_sync(run_migrations)

    yield

    # Teardown
    await sessionmanager.dispose()


# Each test function is a clean slate
@pytest.fixture(scope="function", autouse=True)
async def transactional_session():
    async with sessionmanager.session_factory() as session:
        try:
            await session.begin()
            yield session
        except:
            ...
        # finally:
        #     await session.rollback()  # Rolls back the outer transaction


@pytest.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, db_session):
    async def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[db_helper.get_session_getter] = get_db_session_override


from sqlalchemy import text  # ← Add this import


@pytest.fixture(scope="function", autouse=True)
async def clean_db(db_session):
    """Nuclear option - delete all data after every test"""
    yield

    # Use SQLAlchemy text() for raw SQL
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
    await db_session.commit()
