from fastapi import APIRouter, HTTPException

from socials_api.api.models.database import comment_db, db, post_db
from socials_api.api.routes.user_comments import delete_comments_by_post_id
from socials_api.api.schema.user_posts import (
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)

router = APIRouter(prefix="/post", tags=["user posts"])


# Create Posts
@router.post("", response_model=UserPostOut, status_code=201)
async def create_post(post: UserPostIn):
    """Create social post."""
    # either of both methods work...
    # Method 1...
    # q = post_db.insert().values(post.model_dump())
    # last_post_id = await db.execute(q)
    # Method 2...
    q = post_db.insert()
    post_id = await db.execute(q, post.model_dump())

    return {**(post.model_dump()), "id": post_id}


# Get All Posts
@router.get("/all", response_model=list[UserPostOut])
async def get_all_posts() -> list[UserPostOut]:
    q = post_db.select()
    posts = await db.fetch_all(q)

    if not posts:
        return []

    return posts


# Get All Posts with Comments
@router.get("/all/comments", response_model=list[UserPostWithComments])
async def get_all_posts_with_comments():
    """Get all posts with comments."""
    # fetch posts
    q = post_db.select()
    all_posts = await db.fetch_all(q)
    # if not all_posts:
    #     return []

    # fetch comments
    q = comment_db.select()
    all_comments = await db.fetch_all(q)

    result = [
        {
            "post": {"body": post.body, "id": post.id},
            "comments": [
                {"id": comment.id, "comment": comment.comment}
                for comment in all_comments
                if comment.post_id == post.id
            ],
        }
        for post in all_posts
    ]
    return result


# Get Post by ID
@router.get("/{id}", response_model=UserPostOut)
async def get_post_by_id(id: int) -> UserPostOut:
    q = post_db.select().where(post_db.c.id == id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    return post


# Update Post by ID
@router.put("/{id}", response_model=UserPostOut)
async def update_post_by_id(id: int, new_post: UserPostIn) -> UserPostOut:
    # check if post exists
    q = post_db.select().where(post_db.c.id == id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    # update post in db
    q_update_post = (
        post_db.update().where(post_db.c.id == id).values(body=new_post.body)
    )
    await db.execute(q_update_post)

    # get updated post
    post = await db.fetch_one(q)

    return post


# Delete Post by ID
@router.delete("/{id}")
async def delete_post_by_id(id: int):
    """Delete post by id. Also delete post_id from comment database."""
    q = post_db.select().where(post_db.c.id == id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    try:
        # delete comments associated with post
        comments_update = await delete_comments_by_post_id(id)
    except HTTPException:
        return {
            "message": f"Post with id ({id}) deleted successfully!",
            "post_comments": {"has_comments": False},
        }
    finally:
        q = post_db.delete().where(post_db.c.id == id)
        await db.execute(q)

    return {
        "message": f"Post with id ({id}) deleted successfully!",
        "post_comments": {"has_comments": True, **comments_update},
    }
