import databases
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Table

from socials_api.config import config

# connectivity engine/factory to connect to target db ('sqlite' in this case)
engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args={"check_same_thread": False}
)

# store information about our db tables
metadata = sqlalchemy.MetaData()

# create post_db
post_db = Table(
    "posts", metadata, Column("id", Integer, primary_key=True), Column("body", String)
)

# create comment_db
comment_db = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("comment", String),
    Column("post_id", ForeignKey("posts.id"), nullable=False),
)

# emit DDL to target db
metadata.create_all(engine)

# connect to database using client-side `databases` package
# I choose to use this instead of SQLAlchemy ORM to learn from using close-to-sql query expressions
db = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK)
