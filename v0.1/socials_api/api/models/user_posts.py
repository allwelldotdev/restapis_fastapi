from typing import Annotated

post_db: dict[Annotated[int, "post_id"], Annotated[str, "post_body"]] = {}
