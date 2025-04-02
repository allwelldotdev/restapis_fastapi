import pytest
from httpx import AsyncClient, Response

# Posts
# -------------------------------->8-----------------------------------


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
async def created_post_param(request, async_client: AsyncClient):
    """Parameterized fixture for create_post function."""
    return await create_post(request.param, async_client)


# Using Fixture Factories :: Fixture factory for creating posts
@pytest.fixture  # similar to @pytest.fixture()
def created_post_factory(async_client: AsyncClient):
    """Fixture factory for create_post function. To enable passing of arguments when
    async func (create_post) is called."""

    async def _create_post(body: str = "Test Post"):
        "Call create_post function with params."
        return await create_post(body, async_client)

    return _create_post


# Comments
# -------------------------------->8-----------------------------------


async def create_comments(
    post_id, body: str, async_client: AsyncClient, is_active: bool
) -> Response:
    if is_active:
        response = await async_client.post(
            "/comment", json={"post_id": post_id, "body": body}
        )
        return response
    else:
        pass


# Parameterized fixture for comments, depending on a post
@pytest.fixture(params=[True, False])
async def created_comments_param(
    request, created_post_factory, async_client: AsyncClient
):
    post = await created_post_factory("Test Post for Comments")
    post_id = post["id"]
    return await create_comments(
        post_id, "New Test Comment", async_client, request.param
    )


@pytest.fixture
def created_comment_factory(created_post_factory, async_client: AsyncClient):
    async def _create_comments(
        post_id: int, body: str = "New Test Comment", is_active: bool = True
    ):
        return await create_comments(post_id, body, async_client, is_active)

    return _create_comments
