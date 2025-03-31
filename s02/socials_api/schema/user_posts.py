from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    id: int
