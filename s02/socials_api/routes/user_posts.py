from fastapi import APIRouter, HTTPException

from ..models.user_posts import post_db
from ..schema.user_posts import UserPostIn, UserPostOut

router = APIRouter(prefix="/post", tags=["user posts"])


# Create Posts
@router.post("/", response_model=UserPostOut, status_code=201)
async def create_post(post: UserPostIn):
    """Create social post."""
    # set post id with multiple variations to avoid duplication of id values
    if post_db:
        all_post_ids = set(post_db.keys())
        if len(post_db) in all_post_ids:
            post_id = max(all_post_ids) + 1
        else:
            post_id = len(post_db)
    else:
        post_id = len(post_db)  # 0

    post_db[post_id] = post.body
    return {**(post.model_dump()), "id": post_id}


# Get All Posts
@router.get("/all", response_model=list[UserPostOut])
async def get_all_posts() -> list[UserPostOut]:
    if not post_db:
        raise HTTPException(status_code=404, detail="No post in database.")

    return [
        {"id": post_id, "body": post_body} for post_id, post_body in post_db.items()
    ]


# Get Post by ID
@router.get("/{id}", response_model=UserPostOut)
async def get_post_by_id(id: int) -> UserPostOut:
    if id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not in database.")
    return {"id": id, "body": post_db[id]}


# Update Post by ID
@router.put("/{id}", response_model=UserPostOut)
async def update_post_by_id(id: int, post: UserPostIn) -> UserPostOut:
    if id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    data = post.model_dump()
    post_db[id] = post.body
    updated_post = {**data, "id": id}
    return updated_post


# Delete Post by ID
@router.delete("/{id}")
async def delete_post_by_id(id: int) -> dict[str, str]:
    if id not in post_db:
        raise HTTPException(status_code=404, detail="Post id not in database.")

    del post_db[id]
    return {"message": f"Post with id ({id}) deleted successfully!"}
