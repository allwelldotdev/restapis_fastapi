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
        "/comment", json={"post_id": created_post["id"], "body": "Test Comment"}
    )
    assert response.status_code == 201
    comment_id = response.json()["comments"][0]["id"]

    # grab post id from post_db
    q = post_db.select()
    post = await db.fetch_one(q)
    assert {
        "post": {"body": post.body, "id": post.id},
        "comments": [{"id": comment_id, "comment": "Test Comment"}],
    }.items() <= response.json().items()


# Test post_comments with nonexistent post id
@pytest.mark.anyio
async def test_post_comments_with_nonexistent_post_id(async_client: AsyncClient):
    "Test if post_comments handles no post id."
    random_number = random.randint(10, 20)
    response = await async_client.post(
        "/comment", json={"post_id": random_number, "body": "Test Comment"}
    )
    assert response.status_code == 400  # Bad Request
    assert response.json()["detail"] == "Cannot comment on post_id that does not exist."


# Test get_all_comments
@pytest.mark.anyio
async def test_get_all_comments(
    created_post, created_comment_factory, async_client: AsyncClient
):
    """Test get_all_comments."""
    comments = []
    for _ in range(2):
        response = await created_comment_factory(created_post["id"], "Test Comment")
        # check if comments are created
        assert response.status_code == 201
        comments.append(response)

    response = await async_client.get("/comment/all")
    assert response.status_code == 200

    # check if comment was posted on the appropriate post_id
    assert created_post["id"] == response.json()[0]["post"]["id"]

    # check if all the comments are returned from GET
    comment_1 = comments[0].json()["comments"][0]
    comment_2 = comments[1].json()["comments"][-1]
    assert [comment_1, comment_2] == response.json()[0]["comments"]


# Test get_all_comments with exceptions
@pytest.mark.parametrize("no_post", [True, False])
@pytest.mark.anyio
async def test_get_all_comments_with_exceptions(
    created_post_factory, no_post, async_client: AsyncClient
):
    """Test if get_all_comments can handle no post or no comments."""
    # test no post and no commments
    if no_post:
        response = await async_client.get("/comment/all")
        assert response.status_code == 404
        assert response.json()["detail"] == "No post no comments."
    # test post with no comments
    else:
        await created_post_factory()
        response = await async_client.get("/comment/all")
        assert response.status_code == 404
        assert response.json()["detail"] == "Comments not found."


# Test get_comment_by_post_id
@pytest.mark.anyio
async def test_get_comment_by_post_id(
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
    comment_1 = comments[0].json()["comments"][0]
    comment_2 = comments[1].json()["comments"][0]

    # test get_comment_by_post_id for post with comments
    response = await async_client.get(f"/comment/{post_id_with_comments}")
    assert response.status_code == 200
    assert {
        "post": {
            "id": post_id_with_comments,
            "body": "Test Post 1",
        },
        "comments": [comment_1, comment_2],
    }.items() <= response.json().items()

    # test get_comment_by_post_id for post without comments
    response = await async_client.get(f"/comment/{post_id_no_comments}")
    assert response.status_code == 200
    assert {
        "post": {
            "id": post_id_no_comments,
            "body": "Test Post 2",
        },
        "comments": [],
    }.items() <= response.json().items()


# Test modify_comment by comment id
@pytest.mark.anyio
async def test_modify_comment(
    created_post, created_comment_factory, async_client: AsyncClient
):
    """Test modify_comment."""
    # grab created post id
    post_id = created_post["id"]
    # create comment using post id
    response: Response = await created_comment_factory(post_id, "Test Comment")
    comment_id = response.json()["comments"][0]["id"]
    former_comment_body = response.json()["comments"][0]["comment"]

    # call put method on client, run modify_comment func, grab response
    response = await async_client.put(
        f"/comment/{comment_id}", params={"body": "UPDATED: Test Comment"}
    )
    assert response.status_code == 200
    new_comment_body = response.json()["comments"][0]["comment"]
    assert former_comment_body != new_comment_body
    assert {
        "id": comment_id,
        "comment": "UPDATED: Test Comment",
    }.items() <= response.json()["comments"][0].items()


# Test modify_comment with exceptions
@pytest.mark.anyio
async def test_modify_comment_with_exceptions(
    created_post, created_comment, async_client: AsyncClient
):
    """Test if modify_comment func handles exceptions."""
    random_number = random.randint(10, 20)
    response = await async_client.put(
        f"/comment/{random_number}", params={"body": "UPDATED: Test Comment"}
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
    assert [] == response.json()["comments"]


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
    comment_id = created_comment.json()["comments"][0]["id"]

    # call delete method: delete_comment_by_comment_id
    response = await async_client.delete(f"/comment/{comment_id}")
    # assert comment has been deleted
    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully!"
    # call get method: get_comments_by_post_id
    response = await async_client.get(f"/comment/{post_id}")
    assert response.status_code == 200
    assert [] == response.json()["comments"]


# Test delete_comment_by_comment_id with exceptions
@pytest.mark.anyio
async def test_delete_comment_by_comment_id_with_exceptions(
    created_post, created_comment, async_client: AsyncClient
):
    """Test if delete_comment_by_comment_id handles exceptions."""
    random_number = random.randint(10, 20)
    response = await async_client.delete(f"/comment/{random_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found."
