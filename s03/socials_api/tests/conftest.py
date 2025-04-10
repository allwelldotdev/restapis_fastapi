import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# from socials_api.api.models.user_comments import comment_db
# from socials_api.api.models.user_posts import post_db
from socials_api.api.models.database import db as database

# overwrite .env file value "ENV_STATE" to "test" for db test purposes
os.environ["ENV_STATE"] = "test"

# comment 'noqa: E402' on import line to make Ruff not format the import line
from socials_api.main import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    """Set async backend to run on asyncio."""
    return "asyncio"


@pytest.fixture  # similar to @pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    """Create db fixture to empty (clear) db before each test run."""
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture  # similar to @pytest.fixture()
async def async_client(client: TestClient) -> AsyncGenerator:
    """Get async client with which to make HTTP requests."""
    async with AsyncClient(
        # using transport=ASGITransport from httpx is more recent and recommended than
        # using app=app; although it works but for dated codebases
        transport=ASGITransport(app=app),
        base_url=client.base_url,
    ) as ac:
        yield ac
