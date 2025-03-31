from fastapi import FastAPI

from .models.user_posts import post_table
from .routes import user_comments, user_posts
from .schema.user_posts import UserPostIn, UserPostOut

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


@app.post("/", response_model=UserPostOut)
async def create_post(post: UserPostIn):
    # dumps the json pydantic object into a dict, stores in data
    data = post.model_dump()

    last_post_id = len(post_table)
    post_table[last_post_id] = data
    new_post = {**data, "id": last_post_id}
    return new_post


app.include_router(user_posts.router)
app.include_router(user_comments.router)
