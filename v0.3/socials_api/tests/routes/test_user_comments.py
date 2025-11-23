import random

import pytest
from httpx import AsyncClient, Response

from socials_api.api.models.database import db, post_db
from socials_api.tests.utils import created_comment as _created_comment
from socials_api.tests.utils import created_comment_factory as _created_comment_factory
from socials_api.tests.utils import created_post as _created_post
from socials_api.tests.utils import created_post_factory as _created_post_factory

# set fixture variables
created_post = _created_post
created_post_factory = _created_post_factory
created_comment_factory = _created_comment_factory
created_comment = _created_comment


# Test post_comments
@pytest.mark.anyio
async def test_post_comments(created_post, async_client: AsyncClient):
    """Test post_comments."""
    response = await async_client.post(
        "/comment", json={"post_id": created_post["id"], "comment": "Test Comment"}
    )
    assert response.status_code == 201
    comment_id, comment_body, post_id = (
        response.json()["id"],
        response.json()["comment"],
        created_post["id"],
    )

    assert {
        "id": comment_id,
        "comment": comment_body,
        "post_id": post_id,
    }.items() <= response.json().items()


# Test post_comments with nonexistent post id
@pytest.mark.anyio
async def test_post_comments_with_nonexistent_post_id(async_client: AsyncClient):
    "Test if post_comments handles no post id."
    random_number = random.randint(10, 20)
    response = await async_client.post(
        "/comment", json={"post_id": random_number, "comment": "Test Comment"}
    )
    assert response.status_code == 400  # Bad Request
    assert response.json()["detail"] == "Cannot comment on post_id that does not exist."


# Test get_all_comments
@pytest.mark.anyio
async def test_get_all_comments(
    created_post, created_comment: Response, async_client: AsyncClient
):
    """Test get_all_comments."""
    comment_id, comment_body, post_id = (
        created_comment.json()["id"],
        created_comment.json()["comment"],
        created_comment.json()["post_id"],
    )

    response = await async_client.get("/comment/all")
    assert response.status_code == 200
    assert [
        {"id": comment_id, "comment": comment_body, "post_id": post_id}
    ] == response.json()


# Test get_all_comments with no comment in db
@pytest.mark.anyio
async def test_get_all_comments_with_exceptions(async_client: AsyncClient):
    """Test if get_all_comments can handle no comments."""
    response = await async_client.get("/comment/all")
    assert response.status_code == 200
    assert [] == response.json()


# Test get_comments_by_post_id
@pytest.mark.anyio
async def test_get_comments_by_post_id(
    created_post_factory, created_comment_factory, async_client: AsyncClient
):
    """Test get_comment_by_post_id"""

    # create posts
    posts = []
    for i in range(2):
        response = await created_post_factory(f"Test Post {i + 1}")
        # check if posts are created
        q = post_db.select()
        post = await db.fetch_one(q)
        assert post
        posts.append(response)
    # grab post_id for first post
    post_id_with_comments = posts[0]["id"]
    post_id_no_comments = posts[1]["id"]

    # create comments
    comments = []
    for i in range(2):
        response: Response = await created_comment_factory(
            post_id=post_id_with_comments,
            body=f"Post {post_id_with_comments}: Test Comment {i + 1}",
        )
        # check if comments are created
        assert response.status_code == 201
        comments.append(response)
    # grab comments
    comment_1 = comments[0].json()
    comment_2 = comments[1].json()

    # test get_comment_by_post_id for post with comments
    response = await async_client.get(f"/comment/{post_id_with_comments}")
    assert response.status_code == 200
    assert [comment_1, comment_2] == response.json()

    # test get_comment_by_post_id for post without comments
    response = await async_client.get(f"/comment/{post_id_no_comments}")
    assert response.status_code == 200
    assert [] == response.json()


# Test modify_comment by comment id
@pytest.mark.anyio
async def test_modify_comment(
    created_post, created_comment: Response, async_client: AsyncClient
):
    """Test modify_comment."""
    # grab created post id
    post_id = created_post["id"]
    # grab created comment id and body
    comment_id, former_comment_body = (
        created_comment.json()["id"],
        created_comment.json()["comment"],
    )

    # call put method on client, run modify_comment func, grab response
    response = await async_client.put(
        f"/comment/{comment_id}", params={"comment_body": "UPDATED: Test Comment"}
    )
    assert response.status_code == 200
    new_comment_body = response.json()["comment"]
    assert former_comment_body != new_comment_body
    assert {
        "id": comment_id,
        "comment": "UPDATED: Test Comment",
        "post_id": post_id,
    }.items() <= response.json().items()


# Test modify_comment with exceptions
@pytest.mark.anyio
async def test_modify_comment_with_exceptions(async_client: AsyncClient):
    """Test if modify_comment func handles exceptions."""
    random_number = random.randint(10, 20)
    response = await async_client.put(
        f"/comment/{random_number}", params={"comment_body": "UPDATED: Test Comment"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment id not found."


# Test delete_comments_by_post_id
@pytest.mark.anyio
async def test_delete_comments_by_post_id(
    created_post, created_comment_factory, async_client: AsyncClient
):
    """Test delete_comments_by_post_id."""
    post_id = created_post["id"]
    # create two comments for post_id
    for i in range(2):
        response = await created_comment_factory(post_id, f"Test Comment {i + 1}")

    # call delete method function on created post
    response = await async_client.delete(f"/comment/post/{post_id}")
    # assert post comments are deleted
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == f"All comments on post_id ({post_id}) have been deleted successfully."
    )

    # check if post has any comments: it should not - empty list
    response = await async_client.get(f"/comment/{post_id}")
    assert response.status_code == 200
    assert [] == response.json()


# Test delete_comments_by_post_id with exceptions
@pytest.mark.anyio
async def test_delete_comments_by_post_id_with_exceptions(
    created_post_factory, async_client: AsyncClient
):
    """Test if delete_comments_by_post_id func handles exceptions."""
    # check: post id not found
    random_number = random.randint(10, 20)
    response = await async_client.delete(f"/comment/post/{random_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post id not found."

    # check: post does not have any comments
    response = await created_post_factory()
    post_id = response["id"]

    # call delete method: delete_comments_by_post_id
    response = await async_client.delete(f"/comment/post/{post_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post does not have comments."


# Test delete_comment_by_comment_id
@pytest.mark.anyio
async def test_delete_comment_by_comment_id(
    created_post, created_comment: Response, async_client: AsyncClient
):
    """Test delete_comment_by_comment_id."""
    post_id = created_post["id"]
    comment_id = created_comment.json()["id"]

    # call delete method: delete_comment_by_comment_id
    response = await async_client.delete(f"/comment/{comment_id}")
    # assert comment has been deleted
    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully!"
    # call get method: get_comments_by_post_id
    response = await async_client.get(f"/comment/{post_id}")
    assert response.status_code == 200
    assert [] == response.json()


# Test delete_comment_by_comment_id with exceptions
@pytest.mark.anyio
async def test_delete_comment_by_comment_id_with_exceptions(async_client: AsyncClient):
    """Test if delete_comment_by_comment_id handles exceptions."""
    random_number = random.randint(10, 20)
    response = await async_client.delete(f"/comment/{random_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found."
