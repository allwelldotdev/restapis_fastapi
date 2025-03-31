from fastapi import APIRouter, HTTPException

from ..models.user_posts import post_table
from ..schema.user_posts import UserPostIn, UserPostOut

router = APIRouter(prefix="/posts", tags=["user posts"])


@router.get("/", response_model=list[UserPostOut])
async def get_all_posts():
    if not post_table:
        raise HTTPException(status_code=404, detail="No post in database.")

    return [
        {"id": post_id, "body": post_body["body"]}
        for post_id, post_body in post_table.items()
    ]


@router.get("/id/{id}", response_model=UserPostOut)
async def get_post_by_id(id: int):
    if id not in post_table:
        raise HTTPException(status_code=404, detail="Post id not in database.")
    return UserPostOut(body=post_table[id]["body"], id=id)


@router.delete("/id/{id}")
async def delete_post_by_id(id: int):
    if id not in post_table:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    del post_table[id]
    return {"message": f"Post with id ({id}) deleted successfully!"}


@router.put("/id/{id}", response_model=UserPostOut)
async def update_post_by_id(id: int, body: UserPostIn):
    if id not in post_table:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    data = body.model_dump()
    post_table[id] = data
    updated_post = {**data, "id": id}
    return updated_post
