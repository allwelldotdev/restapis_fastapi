from contextlib import asynccontextmanager

from fastapi import FastAPI

from socials_api.api.models.database import db
from socials_api.api.routes.user_comments import router as user_comments
from socials_api.api.routes.user_posts import router as user_posts


# connect to database before and after request operations
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


app.include_router(user_posts)
app.include_router(user_comments)
