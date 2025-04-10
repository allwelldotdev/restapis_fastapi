from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
