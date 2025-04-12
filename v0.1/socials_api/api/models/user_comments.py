from typing import Annotated

from socials_api.api.schema.user_comments import UserComment

comment_db: dict[
    Annotated[int, "post_id"], Annotated[list[UserComment], "list of comments"]
] = {}
