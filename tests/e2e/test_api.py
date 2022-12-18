import pytest
import requests

from config import get_api_url
from models.category import Category
from models.game import Game
from models.genre import Genre
from services.model_services import ModelService


@pytest.mark.order(3)
@pytest.mark.usefixtures("api")
@pytest.mark.usefixtures("neo4j")
class TestGameAPI:

    @staticmethod
    def _generate_some_games(n=10):
        genres = ["test_genre1", "test_genre2"]
        categories = ["test_category1", "test_category2"]
        instances = [
            ModelService.create_model(Game, **{
                "name": f"entity-{counter}",
                "is_free": False,
                "short_desc": "desc",
                "long_desc": "also desc",
                "header_image": "http://example.com/image",
                "genres": genres if counter < n / 2 else [],
                "categories": categories if counter < n / 2 else [],
            }) for counter in range(n)]
        yield instances

        for genre_name in genres:
            ModelService.delete_model(
                Genre,
                genre_name
            )

        for category_name in categories:
            ModelService.delete_model(
                Category,
                category_name
            )

        for instance in instances:
            ModelService.delete_model(
                Game,
                instance.name
            )
        yield []

    def test_detail_api(self):
        game_data = {
            "name": "Test Game",
            "is_free": False,
            "long_desc": "Detailed description.",
            "short_desc": "short description",
            "date": "23 Aug, 2016",
            "header_image": "https://test.url",
        }

        game = ModelService.create_model(
            Game,
            **game_data
        )

        game_node_id = game.node_id
        response = requests.get(
            f"{get_api_url()}/games/{game_node_id}"
        )

        ModelService.delete_model(
            Game,
            game_data.get("name")
        )

        assert response.status_code == 200
        game_dict = response.json().get("result")

        assert game_dict.get("node_id") == game_node_id
        assert game_dict.get("name") == game_data.get("name")
        assert game_dict.get("long_desc") == game_data.get("long_desc")
        assert game_dict.get("short_desc") == game_data.get("short_desc")
        assert game_dict.get("header_image") == game_data.get("header_image")
        assert game_dict.get("date") == game_data.get("date")

        assert requests.get(
            f"{get_api_url()}/games/{game_node_id}"
        ).status_code == 404

    def test_list_api(self):
        instances_generator = self._generate_some_games(10)
        instances = next(instances_generator)
        instance = instances[0]

        limit = 7
        url = f"{get_api_url()}/games?limit={limit}&sort=-name"
        response = requests.get(url)

        assert response.status_code == 200
        assert len(response.json().get("results")) == limit
        assert response.json().get("previous") is None

        response = requests.get(response.json().get("next"))
        assert response.status_code == 200

        assert len(response.json().get("results")) == len(instances) - limit
        assert response.json().get("next") is None
        next(instances_generator)

    def test_similar_api(self):
        instances_generator = self._generate_some_games(20)
        instances = next(instances_generator)
        instance = instances[0]

        limit = 5
        url = f"{get_api_url()}/games/similar/{instance.node_id}?limit={limit}"
        response = requests.get(url)

        assert response.status_code == 200
        assert len(response.json().get("results")) == limit
        assert response.json().get("previous") is None
        assert response.json().get("next")

        response = requests.get(response.json().get("next"))
        assert response.status_code == 200

        next(instances_generator)
