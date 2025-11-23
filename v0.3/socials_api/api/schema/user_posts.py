from pydantic import BaseModel, ConfigDict

from socials_api.api.schema.user_comments import UserComment


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserPostWithComments(BaseModel):
    post: UserPostOut
    comments: list[UserComment]
