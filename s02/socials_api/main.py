from fastapi import FastAPI

from .routes import user_comments, user_posts

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


app.include_router(user_posts.router)
app.include_router(user_comments.router)
