import random

import pytest
from httpx import AsyncClient

from socials_api.api.models.database import comment_db, db, post_db
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

    # check post_db and grab created post_id
    q = post_db.select()
    post = await db.fetch_one(q)

    assert response.status_code == 201
    assert {"id": post.id, "body": body}.items() <= response.json().items()


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
    response = await async_client.get("/post/all")
    assert response.status_code == 200
    assert response.json() == [created_post]


# Test get_all_posts with no post in db
@pytest.mark.anyio
async def test_get_all_posts_with_empty_database(async_client: AsyncClient):
    """Test for get_all_posts function with exception if no
    post in (empty) database."""
    response = await async_client.get("/post/all")

    # assert post_db is empty
    q = post_db.select()
    posts = await db.fetch_all(q)
    assert not posts

    assert response.status_code == 200
    assert response.json() == []


# Test get_post_by_id
@pytest.mark.anyio
async def test_get_post_by_id(created_post, async_client: AsyncClient):
    """Test get_post_by_id function."""
    # check post_db for post and grab post_id
    q = post_db.select()
    post = await db.fetch_one(q)

    response = await async_client.get(f"/post/{post.id}")
    assert response.status_code == 200
    assert response.json() == created_post


# Test get_post_by_id with nonexistent id
@pytest.mark.anyio
async def test_get_post_by_id_with_nonexistent_id(
    created_post, async_client: AsyncClient
):
    """Test get_post_by_id function."""
    # get random number
    random_number = random.randint(10, 20)

    response = await async_client.get(f"/post/{random_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post id not in database."


# Test update_post_by_id
@pytest.mark.anyio
async def test_update_post_by_id(created_post, async_client: AsyncClient):
    """Test update_post_by_id function."""
    former_post_body, post_id = created_post["body"], created_post["id"]
    response = await async_client.put(
        f"/post/{post_id}", json={"body": "Updated/New Post Body"}
    )
    assert response.status_code == 200
    assert former_post_body != response.json()["body"]
    assert {
        "id": post_id,
        "body": "Updated/New Post Body",
    }.items() <= response.json().items()


# Test update_post_by_id with nonexistent id
@pytest.mark.anyio
async def test_update_post_by_id_with_exceptions(
    created_post, async_client: AsyncClient
):
    """Test if update_post_by_id can handle exceptions."""
    random_number = random.randint(10, 20)
    response = await async_client.put(
        f"/post/{random_number}", json={"body": "Update/New Post Body"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post id not in database."


# Test delete_post_by_id
@pytest.mark.parametrize("has_comments", [True, False])
@pytest.mark.anyio
async def test_delete_post_by_id(
    created_post, created_comment_factory, has_comments, async_client: AsyncClient
):
    """Test delete_post_id function for two scenarios:
    1. Deleting post with comments.
    2. Deleting post without comments."""

    post_id = created_post["id"]  # grab created post id
    q = post_db.select()
    post = await db.fetch_one(q)
    assert post_id == post.id

    if has_comments:
        # create comment on post
        await created_comment_factory(post_id)
        q = comment_db.select().where(comment_db.c.post_id == post.id)
        comment = await db.fetch_one(q)
        assert comment  # confirm comment_db is populated

        # delete post with comments
        delete_post_response = await async_client.delete(f"/post/{post_id}")

        # assert post is deleted
        q = post_db.select().where(post_db.c.id == post.id)
        deleted_post = await db.fetch_one(q)
        assert not deleted_post

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
        delete_post_response = await async_client.delete(f"/post/{post.id}")

        # assert post is deleted
        q = post_db.select().where(post_db.c.id == post.id)
        deleted_post = await db.fetch_one(q)
        assert not deleted_post

        assert delete_post_response.status_code == 200
        assert {
            "message": f"Post with id ({post_id}) deleted successfully!",
            "post_comments": {"has_comments": False},
        }.items() <= delete_post_response.json().items()
