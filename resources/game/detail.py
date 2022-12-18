from flask_restful import Resource, abort

from models.game import Game
from services.model_services import ModelService, ModelNotFoundException


class GameDetailResource(Resource):
    def get(self, node_id):
        try:
            instance = ModelService.get_model(
                Game,
                node_id=node_id
            )
            return {
                "result": instance.serialize()
            }
        except ModelNotFoundException:
            abort(404)
