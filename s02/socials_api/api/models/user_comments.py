from typing import Annotated

from ..schema.user_comments import UserComment

comment_db: dict[
    Annotated[int, "post_id"], Annotated[list[UserComment], "list of comments"]
] = {}
