import pytest
from httpx import AsyncClient

from socials_api.api.models.user_posts import post_db
from socials_api.tests.utils import created_comment_factory as _created_comment_factory
from socials_api.tests.utils import created_post_factory as _created_post_factory

# set fixture variables
created_post_factory = _created_post_factory
created_comment_factory = _created_comment_factory


@pytest.mark.anyio
async def test_post_comments(created_post_factory, async_client: AsyncClient):
    """Test post_comments."""
    post = await created_post_factory("Test Post")
    response = await async_client.post(
        "/comment", json={"post_id": post["id"], "body": "Test Comment"}
    )
    assert response.status_code == 201
    assert {
        "post": {"body": "Test Post", "id": 0},
        "comments": [{"id": 0, "comment": "Test Comment"}],
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_post_comments_without_post_id(async_client: AsyncClient):
    "Test if post_comments handles no post id."
    response = await async_client.post(
        "/comment", json={"post_id": 0, "body": "Test Comment"}
    )
    assert response.status_code == 400  # Bad Request
    assert response.json()["detail"] == "Cannot comment on post_id that does not exist."


@pytest.mark.anyio
async def test_get_all_comments(
    created_post_factory, created_comment_factory, async_client: AsyncClient
):
    """Test get_all_comments."""
    post = await created_post_factory("Test Post")

    comments = []
    for _ in range(2):
        response = await created_comment_factory(post["id"], "Test Comment")
        # check if comments are created
        assert response.status_code == 201
        comments.append(response)
    print(comments)

    response = await async_client.get("/comment/all")
    assert response.status_code == 200

    # check if comment was posted on the appropriate post_id
    assert post["id"] == response.json()[0]["post"]["id"]

    # check if all the comments are returned from GET
    comment_1 = comments[0].json()["comments"][0]
    comment_2 = comments[1].json()["comments"][-1]
    assert [comment_1, comment_2] == response.json()[0]["comments"]


@pytest.mark.parametrize("no_post", [True, False])
@pytest.mark.anyio
async def test_get_all_comments_with_exceptions(
    created_post_factory, no_post, async_client: AsyncClient
):
    """Test if get_all_comments can handle no post or no comments."""
    if no_post:
        response = await async_client.get("/comment/all")
        assert response.status_code == 404
        assert response.json()["detail"] == "No post no comments."
    else:
        await created_post_factory()
        response = await async_client.get("/comment/all")
        assert response.status_code == 404
        assert response.json()["detail"] == "Comments not found."


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
        assert len(post_db) == i + 1
        posts.append(response)
    # grab post_id for first post
    post_id_with_comments = posts[0]["id"]
    post_id_no_comments = posts[1]["id"]
    print(posts)

    # create comments
    comments = []
    for i in range(2):
        response = await created_comment_factory(
            post_id=post_id_with_comments,
            body=f"Post {post_id_with_comments}: Test Comment {i + 1}",
        )
        # check if comments are created
        assert response.status_code == 201
        comments.append(response)
    # grab comments
    comment_1 = comments[0].json()["comments"][0]
    comment_2 = comments[1].json()["comments"][0]
    print(comments)
    print(comment_1)
    print(comments[0].json())

    # test get_comment_by_post_id for post with comments
    response = await async_client.get(f"/comment/{post_id_with_comments}")
    assert response.status_code == 200
    assert {
        "post": {
            "id": post_id_with_comments,
            "body": f"Test Post {post_id_with_comments + 1}",
        },
        "comments": [comment_1, comment_2],
    }.items() <= response.json().items()

    # test get_comment_by_post_id for post without comments
    response = await async_client.get(f"/comment/{post_id_no_comments}")
    assert response.status_code == 200
    assert {
        "post": {
            "id": post_id_no_comments,
            "body": f"Test Post {post_id_no_comments + 1}",
        },
        "comments": [],
    }.items() <= response.json().items()
