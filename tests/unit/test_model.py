from abc import ABC, abstractmethod
from datetime import datetime

import pytest

from models.category import Category
from models.company import Company
from models.content import Content
from models.entity import Entity
from models.game import Game
from models.genre import Genre
from tests.conftest import assert_url_is_http


class BaseModelTest(ABC):
    @abstractmethod
    def test_create_instance(self):
        raise NotImplementedError

    @abstractmethod
    def test_delete_instance(self):
        raise NotImplementedError

    @abstractmethod
    def test_connections(self):
        raise NotImplementedError


@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestEntityModel(BaseModelTest):
    DATA = {
        "name": "test_entity"
    }
    model_cls = Entity

    def test_create_instance(self):
        self.model_cls(
            name=self.DATA.get("name")
        ).save()

        entity = Entity.nodes.get_or_none(name=self.DATA.get("name"))
        assert entity is not None
        assert entity.name == self.DATA.get("name")
        entity.delete()

    def test_delete_instance(self):
        entity = Entity(name=self.DATA.get("name"))
        entity.save()

        entity.delete()
        assert Entity.nodes.get_or_none(name=self.DATA.get("name")) is None

    def test_connections(self):
        pass


@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestContentModel(BaseModelTest):
    DATA = TestEntityModel.DATA
    DATA.update({
        "is_free": False,
        "detailed_description": "Detailed description.",
        "short_description": "short description",
        "release_date": {
            "date": "23 Aug, 2016"
        },

        "background_raw": "https://test.url",
        "header_image": "https://test.url",
        "screenshots": [
            {
                "id": 0,
                "path_thumbnail": "https://test.url",
                "path_full": "https://test.url"
            },
            {
                "id": 1,
                "path_thumbnail": "https://test.url",
                "path_full": "https://test.url"
            },
        ],

        "movies": [
            {
                "webm": {
                    "480": "https://test.url",
                    "max": "https://test.url"
                },
                "mp4": {
                    "480": "https://test.url",
                    "max": "https://test.url"
                },
            }
        ],
        "publishers": ["publisher1"],
        "developers": ["developer1", "developer2"],
    })

    model_cls = Content

    def _create_instance(self):
        instance = self.model_cls.nodes.get_or_none(name=self.DATA.get("name"))
        while instance:
            instance.delete()

        instance = self.model_cls(
            name=self.DATA.get("name"),
            is_free=self.DATA.get("is_free"),
            short_desc=self.DATA.get("short_description"),
            long_desc=self.DATA.get("detailed_description"),
            header_image=self.DATA.get("header_image"),
            images=[image.get("path_full") for image in self.DATA.get("screenshots")],
            movies=[image.get("mp4").get("max") for image in self.DATA.get("movies")]
        )
        instance.save()
        return instance

    def test_create_instance(self):
        instance = self._create_instance()

        assert instance.short_desc == self.DATA.get("short_description")
        assert instance.long_desc == self.DATA.get("detailed_description")
        date = datetime.strptime(self.DATA.get("release_date").get("date"), "%d %b, %Y"),
        assert instance.header_image == self.DATA.get("header_image")

        for image in instance.images:
            assert_url_is_http(image)
        for movie in instance.movies:
            assert_url_is_http(movie)

        instance.delete()

    def test_connections(self):
        instance = self._create_instance()

        publishers = [Company(name=publisher_name) for publisher_name in self.DATA.get("publishers")]
        [publisher.save() for publisher in publishers]
        developers = [Company(name=developers_name) for developers_name in self.DATA.get("developers")]
        [developers.save() for developers in developers]

        for publisher in publishers:
            instance.publishers.connect(publisher)
            assert instance.publishers.relationship(publisher)

        for developer in developers:
            instance.developers.connect(developer)
            assert instance.developers.relationship(developer)

        [developer.delete() for developer in instance.developers]
        [publisher.delete() for publisher in instance.publishers]
        instance.delete()

    def test_delete_instance(self):
        instance = self._create_instance()
        instance.delete()
        assert Content.nodes.get_or_none(name=self.DATA.get("name")) is None


@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestGameModel(TestContentModel):
    DATA = TestContentModel.DATA
    DATA.update({
        "genres": [
            {"id": 0, "description": "genre1"},
            {"id": 1, "description": "genre2"}
        ],
        "categories": [
            {"id": 0, "description": "category1"},
            {"id": 1, "description": "category2"}
        ],
    })
    model_cls = Game

    def test_connections(self):
        instance = self._create_instance()
        genres = [Genre(name=genre.get("description")) for genre in self.DATA.get("genres")]
        [genre.save() for genre in genres]
        categories = [Category(name=category.get("description")) for category in self.DATA.get("genres")]
        [category.save() for category in categories]

        for genre in genres:
            instance.genres.connect(genre)
            assert instance.genres.relationship(genre)

        for category in categories:
            instance.categories.connect(category)
            assert instance.categories.relationship(category)

        [genre.delete() for genre in instance.genres]
        [category.delete() for category in instance.categories]
        instance.delete()
