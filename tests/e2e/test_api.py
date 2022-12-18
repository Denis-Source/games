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
    SOME_GAMES_AMOUNT = 10

    @pytest.fixture
    def some_games(self):
        genres = ["test_genre1", "test_genre2"]
        categories = ["test_category1", "test_category2"]
        instances = [
            ModelService.create_model(Game, **{
                "name": f"entity-{counter}",
                "is_free": False,
                "short_desc": "desc",
                "long_desc": "also desc",
                "header_image": "http://example.com/image",
                "genres": genres if counter < self.SOME_GAMES_AMOUNT / 2 else [],
                "categories": categories if counter < self.SOME_GAMES_AMOUNT / 2 else [],
            }) for counter in range(self.SOME_GAMES_AMOUNT)]

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

    def test_detail_api(self, some_games):
        game = some_games[0]

        response = requests.get(
            f"{get_api_url()}/games/{game.node_id}"
        )
        assert response.status_code == 200
        game_dict = response.json().get("result")

        assert game_dict.get("node_id") == game.node_id
        assert game_dict.get("name") == game.name
        assert game_dict.get("short_desc") == game.short_desc
        assert game_dict.get("long_desc") == game.long_desc
        assert game_dict.get("header_image") == game.header_image
        assert game_dict.get("date") == game.get_formatted_date()

        ModelService.delete_model(
            Game,
            name=game.name
        )

        assert requests.get(
            f"{get_api_url()}/games/{game.node_id}"
        ).status_code == 404

    def test_list_api(self, some_games):
        limit = 7
        url = f"{get_api_url()}/games?limit={limit}&sort=-name"
        response = requests.get(url)

        assert response.status_code == 200
        assert len(response.json().get("results")) == limit
        assert response.json().get("previous") is None
        assert self.SOME_GAMES_AMOUNT - len(response.json().get("results")) < limit

        response = requests.get(response.json().get("next"))
        assert response.status_code == 200
        assert len(response.json().get("results")) == len(some_games) - limit
        assert response.json().get("next") is None

    def test_similar_api(self, some_games):
        based_on_game = some_games[0]

        limit = 5
        url = f"{get_api_url()}/games/similar/{based_on_game.node_id}?limit={limit}"
        response = requests.get(url)

        assert response.status_code == 200
        assert len(response.json().get("results")) == self.SOME_GAMES_AMOUNT / 2 - 1
        assert response.json().get("previous") is None
        assert response.json().get("next")

        response = requests.get(response.json().get("next"))
        assert response.status_code == 200
