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
    def test_create_instance(self, instance):
        raise NotImplementedError

    @abstractmethod
    def test_delete_instance(self, instance):
        raise NotImplementedError

    @abstractmethod
    def test_connections(self, connected_instance):
        raise NotImplementedError

    @pytest.fixture
    def instance(self):
        raise NotImplementedError

    @pytest.fixture
    def connected_instance(self):
        raise NotImplementedError


@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestEntityModel(BaseModelTest):
    DATA = {
        "name": "test_entity"
    }
    model_cls = Entity

    @pytest.fixture
    def instance(self):
        instance_ = self.model_cls(
            **self.DATA
        ).save()

        yield instance_

        try:
            instance_.delete()
        except ValueError:
            pass

    def test_create_instance(self, instance):
        entity = instance
        assert entity is not None
        assert entity.name == self.DATA.get("name")

    def test_delete_instance(self, instance):
        entity = instance

        entity.delete()
        entity = self.model_cls.nodes.get_or_none(name=self.DATA.get("name"))
        assert entity is None

    @pytest.fixture
    def connected_instance(self):
        pass

    def test_connections(self, connected_instance):
        pass



@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestContentModel(TestEntityModel):
    model_cls = Content

    DATE = "23 Aug, 2016"
    DATA = {
        "name": "test_content",
        "is_free": False,
        "short_desc": "short description",
        "long_desc": "Detailed description.",
        "date": datetime.strptime(DATE, model_cls.DATE_FORMAT),

        "header_image": "https://test.url",
        "images": ["https://test.url/image1.jepeh", "https://test.url/image2.jepeh", "https://test.url/image3.jepeh"],
        "movies": ["https://test.url/movie1.empe4", "https://test.url/movie2.empe4"],
    }

    DEVELOPERS = ["developer1", "developer2"]
    PUBLISHERS = ["publisher1"]

    def test_create_instance(self, instance):
        assert instance.short_desc == self.DATA.get("short_desc")
        assert instance.long_desc == self.DATA.get("long_desc")
        assert instance.header_image == self.DATA.get("header_image")

        for image in instance.images:
            assert_url_is_http(image)
        for movie in instance.movies:
            assert_url_is_http(movie)

    @pytest.fixture
    def connected_instance(self, instance):
        publishers = [Company(name=p_name) for p_name in self.PUBLISHERS]
        for publisher in publishers:
            publisher.save()
            instance.publishers.connect(publisher)

        developers = [Company(name=d_name) for d_name in self.DEVELOPERS]
        for developer in developers:
            developer.save()
            instance.developers.connect(developer)

        yield instance, developers, publishers

        [publisher.delete() for publisher in publishers]
        [developer.delete() for developer in developers]

    def test_correct_date_format(self, instance):
        assert instance.get_formatted_date() == self.DATE

    def test_connections(self, connected_instance):
        content, developers, publishers = connected_instance
        for developer in developers:
            assert content.developers.relationship(developer)

            for publisher in publishers:
                assert content.publishers.relationship(publisher)
                assert content.developers.relationship(publisher) is None


@pytest.mark.order(1)
@pytest.mark.usefixtures("neo4j")
class TestGameModel(TestContentModel):
    DATA = TestContentModel.DATA
    DATA.update({
        "name": "test_game",
    })
    GENRES = ["genres1", "genres2"]
    CATEGORIES = ["category1", "category2"]
    model_cls = Game

    @pytest.fixture
    def connected_instance(self, instance):
        genres = [Genre(name=g_name) for g_name in self.GENRES]
        categories = [Category(name=c_name) for c_name in self.CATEGORIES]

        for genre in genres:
            genre.save()
            instance.genres.connect(genre)

        for category in categories:
            category.save()
            instance.categories.connect(category)

        yield instance, genres, categories

        [category.delete() for category in categories]
        [genre.delete() for genre in genres]

    def test_connections(self, connected_instance):
        content, genres, categories = connected_instance
        for genre in genres:
            assert content.genres.relationship(genre)

            for category in categories:
                assert content.categories.relationship(category)
                with pytest.raises(ValueError):
                    content.genres.relationship(category)
