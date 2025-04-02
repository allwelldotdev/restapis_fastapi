import pytest
from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient) -> dict[str, str]:
    response = await async_client.post("/post", json={"body": body})
    return response.json()


# Simple Fixture
@pytest.fixture  # similar to @pytest.fixture()
async def created_post(async_client: AsyncClient):
    """Simple fixture to call create_post function."""
    return await create_post("Test Post", async_client)


# Using Parameterized Fixtures
@pytest.fixture(params=["Test Post 1", "Test Post 2"])
async def created_post_PF(request, async_client: AsyncClient):
    """Parameterized fixture for create_post function."""
    return await create_post(request.param, async_client)


# Using Fixture Factories
@pytest.fixture  # similar to @pytest.fixture()
def created_post_FF(async_client: AsyncClient):
    """Fixture factory for create_post function. To enable passing of arguments when
    async func (create_post) is called."""

    async def _create_post(body: str = "Test Post"):
        "Call create_post function with params."
        return await create_post(body, async_client)

    return _create_post


@pytest.mark.anyio
async def test_creat_post(async_client: AsyncClient):
    """Test create_post function."""
    body = "Test Post"
    response = await async_client.post("/post", json={"body": body})
    assert response.status_code == 201
    assert {"id": 0, "body": body}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_with_missing_input(async_client: AsyncClient):
    """Test whether create_post function returns error when no body param is passed in."""
    response = await async_client.post("/post", json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post):
    """Test get_all_posts function."""
    # Configure and create post before testing :: Testing using Fixture Factories
    # post = await created_post("Test Post 4")
    # print(post)
    # print(created_post) :: Testing using Parameterized Fixtures

    response = await async_client.get("/post/all")
    # print(response.json())
    assert response.status_code == 200
    assert response.json() == [created_post]
