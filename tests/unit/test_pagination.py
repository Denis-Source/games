import pytest

from services.pagination_services import PaginationService


@pytest.mark.order("1")
class TestPagination:
    TEST_URL = "https://example.com/games"

    @staticmethod
    def generate_list():
        return [i for i in range(1000)]

    def test_pagination_limit(self):
        limit = PaginationService.MAX_LIMIT
        list_ = self.generate_list()
        result = PaginationService.get_paginated_list(
            PaginationService.trim_list(list_),
            self.TEST_URL,
            len(PaginationService.trim_list(list_)) < len(list_),
            limit=999
        )
        assert len(result.get("results")) == limit

    def test_proper_pagination(self):
        list_ = self.generate_list()

        start = 87
        limit = 76

        result = PaginationService.get_paginated_list(
            PaginationService.trim_list(list_, start, limit),
            self.TEST_URL,
            len(list_),
            start,
            limit
        )

        assert len(result.get("results")) == limit
        assert result.get("results")[0] == list_[87]
        assert result.get("results")[-1] == list_[limit + start - 1]

    def test_url(self):
        list_ = self.generate_list()

        start = 50
        limit = 40

        result = PaginationService.get_paginated_list(
            PaginationService.trim_list(list_, start, limit),
            self.TEST_URL,
            len(PaginationService.trim_list(list_)) < len(list_),
            start,
            limit
        )

        assert f"start={start - limit}" in result.get("previous")
        assert f"start={start + limit}" in result.get("next")

    def test_url_overflow(self):
        list_ = self.generate_list()

        start = 10
        limit = 50

        result = PaginationService.get_paginated_list(
            PaginationService.trim_list(list_, start, limit),
            self.TEST_URL,
            len(PaginationService.trim_list(list_, start, limit)) < len(list_),
            start,
            limit
        )

        assert f"start={0}" in result.get("previous")
        assert f"start={start + limit}" in result.get("next")

        start = len(list_) - 30
        limit = 50

        result = PaginationService.get_paginated_list(
            PaginationService.trim_list(list_, start, limit),
            self.TEST_URL,
            len(list_),
            start,
            limit
        )

        assert len(result.get("results")) == len(list_) - start
