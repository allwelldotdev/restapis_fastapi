from fastapi import APIRouter, HTTPException

from socials_api.api.models.database import comment_db, db, post_db
from socials_api.api.schema.user_comments import UserCommentIn, UserCommentOut

router = APIRouter(prefix="/comment", tags=["user comments"])


# Post Comments
@router.post("", response_model=UserCommentOut, status_code=201)
async def post_comments(input: UserCommentIn):
    """Post comments on a post."""
    # check if comment post_id exists
    q = post_db.select().where(post_db.c.id == input.post_id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(
            status_code=400, detail="Cannot comment on post_id that does not exist."
        )

    # set post comment
    q = comment_db.insert().values({"comment": input.comment, "post_id": post.id})
    comment_id = await db.execute(q)

    return {"id": comment_id, "comment": input.comment, "post_id": post.id}


# Get All Comments
@router.get("/all", response_model=list[UserCommentOut])
async def get_all_comments():
    """Get all post comments."""
    q = comment_db.select()
    all_comments = await db.fetch_all(q)

    return all_comments


# Get Comments by Post ID
@router.get("/{post_id}", response_model=list[UserCommentOut])
async def get_comments_by_post_id(post_id: int):
    """Get comments by post."""
    # check if post exist
    q = post_db.select().where(post_db.c.id == post_id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(status_code=404, detail="Post id not found.")

    q = comment_db.select().where(comment_db.c.post_id == post.id)
    comments = await db.fetch_all(q)

    return comments


# Modify/Update Comment by Comment ID
@router.put("/{comment_id}", response_model=UserCommentOut)
async def modify_comment(comment_id: int, comment_body: str):
    """Modify comment by comment id and post id."""
    # check if comment_id exists
    q = comment_db.select().where(comment_db.c.id == comment_id)
    comment = await db.fetch_one(q)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment id not found.")

    # update comment
    q_update_comment = (
        comment_db.update()
        .where(comment_db.c.id == comment_id)
        .values(comment=comment_body)
    )
    await db.execute(q_update_comment)

    # grab new comment data
    comment = await db.fetch_one(q)
    return comment


# Delete Comments by Post ID
@router.delete("/post/{post_id}")
async def delete_comments_by_post_id(post_id: int):
    """Delete all comments with a post id. Also deletes all post comments from the comment database."""
    # check if post exist
    q = post_db.select().where(post_db.c.id == post_id)
    post = await db.fetch_one(q)
    if not post:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # check if post has comments
    q = comment_db.select().where(comment_db.c.post_id == post_id)
    comments = await db.fetch_all(q)
    if not comments:
        raise HTTPException(status_code=404, detail="Post does not have comments.")

    # delete comments associated to post
    q = comment_db.delete().where(comment_db.c.post_id == post_id)
    await db.execute(q)

    return {
        "message": f"All comments on post_id ({post_id}) have been deleted successfully."
    }


# Delete Comment by Commment ID
@router.delete("/{comment_id}")
async def delete_comment_by_comment_id(comment_id: int):
    """Delete comment by comment id."""
    # check if comment exists
    q = comment_db.select().where(comment_db.c.id == comment_id)
    comment = await db.fetch_one(q)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    # delete comment
    q = comment_db.delete().where(comment_db.c.id == comment_id)
    await db.execute(q)

    return {"message": "Comment deleted successfully!"}
