from typing import Annotated

from pydantic import BaseModel, ConfigDict


class UserCommentIn(BaseModel):
    post_id: Annotated[int, "post_id"]
    comment: Annotated[str, "comment_body"]


class UserComment(BaseModel):
    id: Annotated[int, "comment_id"]
    comment: Annotated[str, "comment_body"]


class UserCommentOut(UserComment):
    post_id: Annotated[int, "post_id"]
    model_config = ConfigDict(from_attributes=True)
