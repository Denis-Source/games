import pytest

from models.category import Category
from models.content import Content
from models.dlc import DLC
from models.entity import Entity
from models.game import Game
from models.genre import Genre
from services.model_services import ModelService


@pytest.mark.order(2)
@pytest.mark.usefixtures("neo4j")
class TestModelService:
    @pytest.fixture
    def instances(self):
        genres_names = ["test_genre1", "test_genre2"]
        categories_names = ["test_category1", "test_category2"]

        instances_ = [
            ModelService.create_model(Game, **{
                "name": f"entity-{counter}",
                "is_free": counter % 3 == 0,
                "short_desc": "desc",
                "long_desc": "also desc",
                "header_image": "https://example.com/image",
                "genres": genres_names if counter % 3 == 0 else [],
                "categories": categories_names if counter % 3 == 0 else [],
            }) for counter in range(10)]

        yield instances_

        for name in genres_names:
            ModelService.delete_model(Genre, name)

        for name in categories_names:
            ModelService.delete_model(Category, name)

        [instance.delete() for instance in instances_]

    @pytest.fixture
    def duplicate_instances(self):
        name = "I am an unique entity"
        instances = [ModelService.create_model(
                model_cls=Entity,
                name=name
            ).save() for _ in range(10)]

        yield instances

        [instance.delete() for instance in instances]

    def test_creation_no_duplicates(self, duplicate_instances):
        example_instance = duplicate_instances[0]
        assert all([instance.name == example_instance.name for instance in duplicate_instances])
        assert all([instance.node_id == example_instance.node_id for instance in duplicate_instances])
        result, _ = ModelService.get_filtered_list(
            example_instance.__class__,
            name=example_instance.name
        )
        assert len(result) == 1

    def test_model_filtered_list(self, instances):
        results, is_next = ModelService.get_filtered_list(Game, is_free=True, limit=10)
        assert len(results) == 4
        assert is_next is False

    def test_model_creation_sad(self):
        model_clss = [Game, DLC, Content]
        data = {
            "name": "test_name",
            "not_usable": "hehe"
        }

        for model_cls in model_clss:
            with pytest.raises(TypeError):
                ModelService.create_model(
                    model_cls=model_cls,
                    name=data.get("name")
                )

    def test_similar_list(self, instances):
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
