from flask import request
from flask_restful import Resource, reqparse

from models.game import Game
from services.model_services import ModelService
from services.pagination_services import PaginationService


class GameListResource(Resource):
    DEFAULT_LIMIT = 10
    DEFAULT_SORT = "-name"
    GET_PARAMS = {
        "start": {
            "default": 0,
            "type": int
        },
        "limit": {
            "default": DEFAULT_LIMIT,
            "type": int
        },
        "sort": {
            "default": DEFAULT_SORT,
            "type": str
        }
    }

    def get(self):
        parser = reqparse.RequestParser()

        for name, value in self.GET_PARAMS.items():
            parser.add_argument(name, default=value["default"], type=value["type"], location="args")

        args = parser.parse_args()

        list_, is_next = ModelService.get_filtered_list(
            model_cls=Game,
            start=args.get("start"),
            limit=args.get("limit"),
            order_by=args.get("sort")
        )

        return PaginationService.get_paginated_list(
            list_=[instance.serialize(connections=True) for instance in list_],
            url=request.base_url,
            is_next=is_next,
            start=args.get("start"),
            limit=args.get("limit")
        )