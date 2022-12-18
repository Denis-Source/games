from flask import request
from flask_restful import Resource, reqparse, abort
from neomodel import db

from models.game import Game

from services.model_services import ModelService, ModelNotFoundException
from services.pagination_services import PaginationService


class GameSimilarResource(Resource):
    DEFAULT_LIMIT = 10
    GET_PARAMS = {
        "start": {
            "default": 0,
            "type": int
        },
        "limit": {
            "default": DEFAULT_LIMIT,
            "type": int
        }
    }

    def get(self, node_id):
        parser = reqparse.RequestParser()
        for name, value in self.GET_PARAMS.items():
            parser.add_argument(name, default=value["default"], type=value["type"], location="args")
        args = parser.parse_args()

        try:
            instance = ModelService.get_model(
                Game,
                node_id=node_id
            )
        except ModelNotFoundException:
            abort(404)

        list_, is_next = ModelService.get_similar_list(
            model_cls=Game,
            name=instance.name,
            start=args.get("start"),
            limit=args.get("limit")
        )

        return PaginationService.get_paginated_list(
            list_=[instance.serialize(connections=True) for instance in list_],
            url=request.base_url,
            is_next=is_next,
            start=args.get("start"),
            limit=args.get("limit")
        )
