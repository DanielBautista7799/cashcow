from typing import Literal

from fastapi import Query


class PageParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        size: int = Query(default=10, ge=1, le=100),
        sort_by: str = Query(default="id"),
        sort_dir: Literal["asc", "desc"] = Query(default="asc"),
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_dir = sort_dir

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
