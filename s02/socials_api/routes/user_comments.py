from fastapi import APIRouter, HTTPException

from ..models.user_comments import comment_table
from ..models.user_posts import post_table
from ..schema.user_comments import UserComment, UserCommentIn, UserComments
from ..schema.user_posts import UserPostOut

router = APIRouter(prefix="/comment", tags=["user comments"])


@router.post("/", response_model=UserComments)
async def post_comments(comment: UserCommentIn):
    """Post comments on a post."""
    if comment.post_id not in post_table:
        raise HTTPException(
            status_code=400, detail="Cannot comment on post_id that does not exist."
        )

    # grab post body from post_table db
    post_body = post_table.get(comment.post_id)["body"]
    # grab comments by post id if set, or set to empty list
    comments_by_post_id = comment_table.get(
        comment.post_id, comment_table.setdefault(comment.post_id, [])
    )
    # set comment id
    comment_id = len(comments_by_post_id)
    # set post comment
    post_comment = UserComment(id=comment_id, comment=comment.body)

    # save comment to comment_table db
    comments_by_post_id.append(post_comment.model_dump())

    # return new comment
    new_comment = UserComments(
        post=UserPostOut(body=post_body, id=comment.post_id), comments=[post_comment]
    )
    return new_comment


@router.get("/all", response_model=list[UserComments])
async def get_all_comments():
    """Get all post comments."""
    if not post_table:
        raise HTTPException(status_code=404, detail="No post no comments.")
    if not comment_table:
        raise HTTPException(status_code=404, detail="Comments not found.")

    result = [
        UserComments(
            post=UserPostOut(
                body=post_table.get(comment_post_id)["body"], id=comment_post_id
            ),
            comments=comment_table.get(comment_post_id),
        )
        for comment_post_id in comment_table
    ]
    return result


@router.get("/{post_id}")
async def get_comments_by_post_id(post_id: int):
    """Get comments by post."""
    if post_id not in post_table:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # grab post body from post_table db
    post_body = post_table.get(post_id)["body"]
    # grab comments by post id if set, or set to empty list
    comments_by_post_id = comment_table.get(
        post_id, comment_table.setdefault(post_id, [])
    )

    # show empty list for comment instead
    # if len(comments_by_post_id) == 0:
    #     raise HTTPException(status_code=404, detail="No comment on this post.")

    return UserComments(
        post=UserPostOut(body=post_body, id=post_id), comments=comments_by_post_id
    )
