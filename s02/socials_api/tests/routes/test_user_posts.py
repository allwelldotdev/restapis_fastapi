import pytest
from httpx import AsyncClient

from socials_api.api.models.user_comments import comment_db
from socials_api.api.models.user_posts import post_db


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
async def test_get_all_posts(created_post, async_client: AsyncClient):
    """Test get_all_posts function."""
    # Configure and create post before testing :: Testing using Fixture Factories
    # post = await created_post("Test Post 4")
    # print(post)
    # print(created_post) :: Testing using Parameterized Fixtures

    response = await async_client.get("/post/all")
    # print(response.json())
    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_get_post_by_id(created_post, async_client: AsyncClient):
    """Test get_post_by_id function."""
    response = await async_client.get("/post/0")
    assert response.status_code == 200
    assert response.json() == created_post


@pytest.mark.anyio
async def test_update_post_by_id(created_post, async_client: AsyncClient):
    former_post_body = created_post["body"]
    response = await async_client.put("/post/0", json={"body": "Updated/New Post Body"})
    assert response.status_code == 200
    assert former_post_body != response.json()["body"]
    assert {"id": 0, "body": "Updated/New Post Body"}.items() <= response.json().items()


@pytest.mark.anyio
async def test_delete_post_by_id(created_post, async_client: AsyncClient):
    post_id = created_post["id"]
    len_of_db_before_del = len(post_db)
    assert post_id in post_db

    response = await async_client.delete("/post/0")

    len_of_db_after_del = len(post_db)
    assert len_of_db_before_del > len_of_db_after_del
    assert post_id not in post_db

    assert response.status_code == 200
    if not comment_db:
        assert {
            "message": f"Post with id ({post_id}) deleted successfully!",
            "post_comments": {"has_comments": False},
        }.items() <= response.json().items()
