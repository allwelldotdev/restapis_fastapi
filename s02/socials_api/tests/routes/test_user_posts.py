import pytest
from httpx import AsyncClient

from socials_api.api.models.user_comments import comment_db
from socials_api.api.models.user_posts import post_db
from socials_api.tests.utils import created_post as _created_post

created_post = _created_post


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
