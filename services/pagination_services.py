from models.base import BaseModel


class PaginationService:
    MAX_LIMIT = 100

    @staticmethod
    def get_paginated_list(
            list_: list,
            url: str,
            is_next: bool = True,
            start: int = 0,
            limit: int = MAX_LIMIT
    ) -> dict:
        if limit > PaginationService.MAX_LIMIT:
            limit = PaginationService.MAX_LIMIT

        paginated = {"start": start, "limit": limit}
        if start == 0:
            paginated["previous"] = None
        else:
            paginated["previous"] = url + f"?start={max(0, start - limit)}&limit={start}"
        if not is_next:
            paginated["next"] = None
        else:
            paginated["next"] = url + f"?start={start + limit}&limit={limit}"

        paginated["results"] = list_
        return paginated

    @staticmethod
    def trim_list(list_: list, start: int = 0, limit: int = MAX_LIMIT):
        if limit > PaginationService.MAX_LIMIT:
            limit = PaginationService.MAX_LIMIT

        return list_[start:(start + limit)]
