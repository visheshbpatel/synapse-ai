
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.config import get_settings
from app.db import get_db
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    settings = get_settings()

    if not settings.test_database_url:
        pytest.fail("TEST_DATABASE_URL must be configured for API tests.")

    test_url = make_url(settings.test_database_url)
    app_url = make_url(settings.database_url)

    if test_url == app_url:
        pytest.fail("Test and development databases must be different.")

    if test_url.get_backend_name() != "postgresql":
        pytest.fail("API tests require PostgreSQL.")

    if test_url.host == app_url.host:
        pytest.fail(
            "Test and development databases must use different Neon branch hosts."
        )

    engine = create_engine(
        settings.test_database_url,
        pool_pre_ping=True,
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        engine.dispose()
        raise

    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()

        session_factory = sessionmaker(
            bind=connection,
            autoflush=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        session = session_factory()

        try:
            yield session
        finally:
            session.close()
            if transaction.is_active:
                transaction.rollback()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
