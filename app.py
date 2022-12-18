from flask import Flask
from flask_restful import Api

from config import *
from resources.game.detail import GameDetailResource
from resources.game.list import GameListResource
from resources.game.similar import GameSimilarResource


def create_app(test_config=None):
    ROUTES = {
        "/games": GameListResource,
        "/games/<string:node_id>": GameDetailResource,
        "/games/similar/<string:node_id>": GameSimilarResource
    }

    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    config.DATABASE_URL = get_neo4j_url()

    for route, resource in ROUTES.items():
        api.add_resource(resource, route)

    @app.errorhandler(404)
    def error(e):
        return {"message": str(e)}, 404

    return app
