import pytest
from httpx import AsyncClient

from socials_api.tests.utils import created_comment_factory as _created_comment_factory
from socials_api.tests.utils import created_post_factory as _created_post_factory

created_post_factory = _created_post_factory
created_comment_factory = _created_comment_factory


@pytest.mark.anyio
async def test_post_comments(created_post_factory, async_client: AsyncClient):
    """Test post_comments function."""
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
async def test_get_all_comments(
    created_post_factory, created_comment_factory, async_client: AsyncClient
):
    """Test get_all_comments function."""
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
