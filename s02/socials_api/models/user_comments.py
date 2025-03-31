from typing import Annotated

from ..schema.user_comments import UserComment

comment_table: Annotated[dict, dict[int, list[UserComment]]] = {}
