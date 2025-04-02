from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from socials_api.api.models.user_comments import comment_db
from socials_api.api.models.user_posts import post_db
from socials_api.main import app


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
    post_db.clear()
    comment_db.clear()
    yield


@pytest.fixture  # similar to @pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    """Get async client with which to make HTTP requests."""
    async with AsyncClient(
        # using transport=ASGITransport from httpx is more recent and recommended than
        # using app=app; although it works but for dated codebases
        transport=ASGITransport(app=app),
        base_url=client.base_url,
    ) as ac:
        yield ac
