from fastapi import FastAPI

from .api.routes.user_comments import router as user_comments
from .api.routes.user_posts import router as user_posts

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


app.include_router(user_posts)
app.include_router(user_comments)
