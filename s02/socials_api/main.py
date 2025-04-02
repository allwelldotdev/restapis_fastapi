from fastapi import FastAPI

from socials_api.api.routes.user_comments import router as user_comments
from socials_api.api.routes.user_posts import router as user_posts

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


app.include_router(user_posts)
app.include_router(user_comments)
