from typing import Annotated

from pydantic import BaseModel

from .user_posts import UserPostOut


class UserCommentIn(BaseModel):
    post_id: Annotated[int, "post_id"]
    body: Annotated[str, "comment_body"]


class UserComment(BaseModel):
    id: Annotated[int, "comment_id"]
    comment: Annotated[str, "comment_body"]


class UserComments(BaseModel):
    post: UserPostOut
    comments: list[UserComment]
