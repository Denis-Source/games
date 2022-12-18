import pytest

from models.category import Category
from models.company import Company
from models.content import Content
from models.dlc import DLC
from models.entity import Entity
from models.game import Game
from models.genre import Genre
from services.model_services import ModelService


@pytest.mark.order(2)
@pytest.mark.usefixtures("neo4j")
class TestModelService:
    def test_creation_no_duplicates(self):
        name = "I am an unique entity"
        for i in range(4):
            instance = ModelService.create_model(
                model_cls=Entity,
                name=name
            )
        results, is_next = ModelService.get_filtered_list(
            model_cls=Entity,
            name=name
        )
        assert is_next is False
        assert len(results) == 1
        instance.delete()

    def test_model_filtered_list(self):
        instances = [
            ModelService.create_model(Game, **{
                "name": f"entity-{counter}",
                "is_free": counter % 3 == 0,
                "short_desc": "desc",
                "long_desc": "also desc",
                "header_image": "http://example.com/image"
            }) for counter in range(10)]

        results, is_next = ModelService.get_filtered_list(Game, is_free=True)
        assert len(results) == 4

        [instance.delete() for instance in instances]

    def test_model_creation_happy(self):
        model_clss = [Entity, Company, Genre, Category]
        data = {
            "name": "test_name",
            "not_usable": "hehe"
        }

        for model_cls in model_clss:
            instance = ModelService.create_model(
                model_cls=model_cls,
                name=data.get("name")
            )
            assert isinstance(instance, model_cls)
            assert instance.name == data.get("name")

            instance.delete()

    def test_model_creation_sad(self):
        model_clss = [Game, DLC, Content]
        data = {
            "name": "test_name",
            "not_usable": "hehe"
        }

        for model_cls in model_clss:
            with pytest.raises(TypeError):
                instance = ModelService.create_model(
                    model_cls=model_cls,
                    name=data.get("name")
                )

    def test_similar_list(self):
        genres_names = ["test_genre1", "test_genre2"]
        categories_names = ["test_category1", "test_category2"]

        instances = [
            ModelService.create_model(Game, **{
                "name": f"entity-{counter}",
                "is_free": False,
                "short_desc": "desc",
                "long_desc": "also desc",
                "header_image": "http://example.com/image",
                "genres": genres_names if counter % 3 == 0 else [],
                "categories": categories_names if counter % 3 == 0 else [],
            }) for counter in range(10)]

        similar_names = [f"entity-{counter}" for counter in range(1, 10, 3)]

        instance = ModelService.get_model(
            Game,
            name=f"entity-{0}"
        )

        limit = 5

        results, _ = ModelService.get_similar_list(
            Game,
            name=instance.name,
            limit=limit
        )

        assert len(results) == len(similar_names)
        for similar in results[:len(similar_names)]:
            assert similar

        for name in genres_names:
            ModelService.delete_model(Genre, name)

        for name in categories_names:
            ModelService.delete_model(Category, name)

        for instance in instances:
            ModelService.delete_model(Game, instance.name)
