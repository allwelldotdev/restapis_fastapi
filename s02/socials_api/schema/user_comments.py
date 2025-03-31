from pydantic import BaseModel

from .user_posts import UserPostOut


class UserCommentIn(BaseModel):
    post_id: int
    body: str


class UserComment(BaseModel):
    id: int
    comment: str


class UserComments(BaseModel):
    post: UserPostOut
    comments: list[UserComment]
