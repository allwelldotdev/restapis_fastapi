import pytest
from httpx import AsyncClient

from socials_api.api.models.user_comments import comment_db
from socials_api.api.models.user_posts import post_db
from socials_api.tests.utils import created_comment_factory as _created_comment_factory
from socials_api.tests.utils import created_post as _created_post

# set fixture variables
created_post = _created_post
created_comment_factory = _created_comment_factory


# Test create_post
@pytest.mark.anyio
async def test_creat_post(async_client: AsyncClient):
    """Test create_post function."""
    body = "Test Post"
    response = await async_client.post("/post", json={"body": body})
    assert response.status_code == 201
    assert {"id": 0, "body": body}.items() <= response.json().items()


# Test create_post with no body
@pytest.mark.anyio
async def test_create_post_with_no_body(async_client: AsyncClient):
    """Test whether create_post function returns error when no body param is passed in."""
    response = await async_client.post("/post", json={})
    # Pydantic validation error
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"


# Test get_all_posts
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


# Test get_all_posts with no post in db
@pytest.mark.anyio
async def test_get_all_posts_with_empty_database(async_client: AsyncClient):
    """Test for get_all_posts function with exception if no
    post in (empty) database."""
    response = await async_client.get("/post/all")
    assert response.status_code == 404
    assert response.json()["detail"] == "No post in database."


@pytest.mark.anyio
async def test_get_post_by_id(created_post, async_client: AsyncClient):
    """Test get_post_by_id function."""
    response = await async_client.get("/post/0")
    assert response.status_code == 200
    assert response.json() == created_post


@pytest.mark.anyio
async def test_get_post_by_id_with_nonexistent_id(
    created_post, async_client: AsyncClient
):
    """Test get_post_by_id function."""
    response = await async_client.get("/post/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post id not in database."


@pytest.mark.anyio
async def test_update_post_by_id(created_post, async_client: AsyncClient):
    former_post_body, former_post_id = created_post["body"], created_post["id"]
    response = await async_client.put("/post/0", json={"body": "Updated/New Post Body"})
    assert response.status_code == 200
    assert former_post_body != response.json()["body"]
    assert former_post_body != post_db.get(former_post_id)
    assert {"id": 0, "body": "Updated/New Post Body"}.items() <= response.json().items()


@pytest.mark.parametrize("has_comments", [True, False])
@pytest.mark.anyio
async def test_delete_post_by_id(
    created_post, created_comment_factory, has_comments, async_client: AsyncClient
):
    """Test delete_post_id function for two scenarios:
    1. Deleting post with comments.
    2. Deleting post without comments."""

    post_id = created_post["id"]  # grab created post id
    len_of_db_before_del = len(post_db)
    assert post_id in post_db

    if has_comments:
        # create comment on post
        await created_comment_factory(post_id)
        assert comment_db  # confirm comment_db is populated

        # delete post with comments
        delete_post_response = await async_client.delete("/post/0")

        # assert post is deleted
        len_of_db_after_del = len(post_db)
        assert len_of_db_before_del > len_of_db_after_del
        assert post_id not in post_db

        assert delete_post_response.status_code == 200
        assert {
            "message": f"Post with id ({post_id}) deleted successfully!",
            "post_comments": {
                "has_comments": True,
                "message": f"All comments on post_id ({post_id}) have been deleted successfully.",
            },
        }.items() <= delete_post_response.json().items()
    else:
        # delete post without comments
        delete_post_response = await async_client.delete("/post/0")

        # assert post is deleted
        len_of_db_after_del = len(post_db)
        assert len_of_db_before_del > len_of_db_after_del
        assert post_id not in post_db

        assert delete_post_response.status_code == 200
        assert {
            "message": f"Post with id ({post_id}) deleted successfully!",
            "post_comments": {"has_comments": False},
        }.items() <= delete_post_response.json().items()
