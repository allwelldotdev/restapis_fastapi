from fastapi import APIRouter, HTTPException

from ..models.user_comments import comment_db
from ..models.user_posts import post_db
from ..schema.user_comments import UserCommentIn, UserComments
from ..schema.user_posts import UserPostOut

router = APIRouter(prefix="/comment", tags=["user comments"])


# Post Comments
@router.post("/", response_model=UserComments, status_code=201)
async def post_comments(comment: UserCommentIn):
    """Post comments on a post."""
    if comment.post_id not in post_db:
        raise HTTPException(
            status_code=400, detail="Cannot comment on post_id that does not exist."
        )

    # grab post body from post_db
    post_body = post_db.get(comment.post_id)
    # grab comments by post id if set, or set to empty list
    comments_list = comment_db.get(
        comment.post_id, comment_db.setdefault(comment.post_id, [])
    )

    # set comment id with multiple variations to avoid duplication of id values
    if comments_list:
        all_comment_ids_by_post = {comment_data["id"] for comment_data in comments_list}
        if len(comments_list) in all_comment_ids_by_post:
            comment_id = max(all_comment_ids_by_post) + 1
        else:
            comment_id = len(comments_list)
    else:
        comment_id = len(comments_list)  # 0

    # set post comment
    comment_data = {"id": comment_id, "comment": comment.body}

    # save comment to comment_db db
    comments_list.append(comment_data)

    # return new comment
    new_comment = UserComments(
        post=UserPostOut(body=post_body, id=comment.post_id), comments=[comment_data]
    )
    return new_comment


# Get All Comments
@router.get("/all", response_model=list[UserComments])
async def get_all_comments():
    """Get all post comments."""
    if not post_db:
        raise HTTPException(status_code=404, detail="No post no comments.")
    if not comment_db:
        raise HTTPException(status_code=404, detail="Comments not found.")

    result = [
        {
            "post": {"body": post_db.get(comment_post_id), "id": comment_post_id},
            "comments": comment_db.get(comment_post_id),
        }
        for comment_post_id in comment_db
    ]
    return result


# Get Comments by Post ID
@router.get("/{post_id}", response_model=UserComments)
async def get_comments_by_post_id(post_id: int):
    """Get comments by post."""
    if post_id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # grab post body from post_db db
    post_body = post_db.get(post_id)

    # if len(comments_by_post_id) == 0:
    #     raise HTTPException(status_code=404, detail="No comment on this post.")

    # show empty list for comment instead
    # grab comments by post id if set, or return an empty list signifying no comments available yet
    comments_list = comment_db.get(post_id, [])

    return UserComments(
        post=UserPostOut(body=post_body, id=post_id), comments=comments_list
    )


# Modify/Update Comment by Comment ID
@router.put("/{comment_id}", response_model=UserComments)
async def modify_comment(comment_id: int, new_comment: UserCommentIn):
    """Modify comment by comment id and post id."""
    # check if post_id is in post_db
    if new_comment.post_id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # check if comment_id exists in all_comment_ids
    all_comment_ids = {
        comments_data["id"]
        for comments_list in comment_db.values()
        for comments_data in comments_list
    }
    if comment_id not in all_comment_ids:
        raise HTTPException(status_code=404, detail="Comment id not found.")

    # get comments_list by post and check if post has any comment
    comments_list = comment_db.get(new_comment.post_id)
    if not comments_list:
        raise HTTPException(
            status_code=404, detail="This post does not have any comments."
        )

    # check if post has specified comment_id
    all_comment_ids_by_post = {
        comment_list["id"] for comment_list in comment_db.get(new_comment.post_id)
    }
    if comment_id not in all_comment_ids_by_post:
        raise HTTPException(
            status_code=404,
            detail=f"This post does not have this comment_id ({comment_id})",
        )

    # update comment_db with new comment
    for comment_data in comments_list:
        if comment_data["id"] == comment_id:
            comment_data["comment"] = new_comment.body
            break

    # grab new comment from comment_db and return
    result = UserComments(
        post=UserPostOut(body=post_db.get(new_comment.post_id), id=new_comment.post_id),
        comments=[{"id": comment_data["id"], "comment": comment_data["comment"]}],
    )

    return result


# Delete Comments by Post ID
@router.delete("/post/{post_id}")
async def delete_comments_by_post_id(post_id: int):
    """Delete all comments to with a post id. Also deletes all post comments from the comment database."""
    # check if post_id is in post_db
    if post_id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # get comments_list by post and check if post has any comment
    comments_list = comment_db.get(post_id)
    if not comments_list:
        raise HTTPException(
            status_code=404, detail="This post does not have any comments."
        )

    # delete post_id along with list of comments from comment_db
    del comment_db[post_id]

    return {
        "message": f"All comments on post_id ({post_id}) have been deleted successfully."
    }


# Delete Comment by Commment ID
@router.delete("/{comment_id}")
async def delete_comment_by_comment_id(comment_id: int, post_id: int):
    """Delete comment by comment id and post id."""
    # check if post_id is in post_db
    if post_id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not found.")

    # check if comment_id exists in all_comment_ids
    all_comment_ids = {
        comment_data["id"]
        for comments_list in comment_db.values()
        for comment_data in comments_list
    }
    if comment_id not in all_comment_ids:
        raise HTTPException(status_code=404, detail="Comment id not found.")

    # get comments_list by post and check if post has any comment
    comments_list = comment_db.get(post_id)
    if not comments_list:
        raise HTTPException(
            status_code=404, detail="This post does not have any comments."
        )

    # check if post has specified comment_id
    all_comment_ids_by_post = {
        comment_list["id"] for comment_list in comment_db.get(post_id)
    }
    if comment_id not in all_comment_ids_by_post:
        raise HTTPException(
            status_code=404,
            detail=f"This post does not have this comment_id ({comment_id})",
        )

    # delete comment from comment_db
    for idx, val in enumerate(comments_list):
        if val["id"] == comment_id:
            del comments_list[idx]

    return {"message": "Comment deleted successfully!"}
