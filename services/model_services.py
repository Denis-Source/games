from datetime import datetime
from typing import List, Tuple

from neomodel import db

from models.base import BaseModel
from models.category import Category
from models.company import Company
from models.content import Content
from models.dlc import DLC
from models.entity import Entity
from models.game import Game
from models.genre import Genre


class ModelNotFoundException(Exception):
    pass


class ModelService:
    @staticmethod
    def get_model(model_cls: type, **kwargs) -> BaseModel:
        instance = model_cls.nodes.get_or_none(**kwargs)
        if not instance:
            raise ModelNotFoundException
        return instance

    @staticmethod
    def get_filtered_list(
            model_cls: type,
            start: int = 0,
            limit: int = None,
            order_by="-name",
            **kwargs
    ) -> Tuple[List[BaseModel], bool]:
        results = model_cls.nodes.filter(**kwargs).order_by(order_by)

        if limit:
            offset = start + limit
        else:
            offset = len(results)

        return results[start:offset], offset < len(results)

    @staticmethod
    def get_cyphered_list(
            model_cls: type,
            cypher: str,
            start: int = 0,
            limit: int = None,
    ) -> Tuple[List[BaseModel], bool]:
        cypher += f"SKIP {start} LIMIT {limit}"
        results, _ = db.cypher_query(cypher)
        results = [model_cls.inflate(row[0]) for row in results]
        start += limit

        next_results, _ = db.cypher_query(cypher)
        return results, len(next_results)

    @staticmethod
    def get_similar_list(
            model_cls: type,
            name: str,
            start: int = 0,
            limit: int = None,
    ):

        cypher_placeholder = "%node_id"
        cypher = f"START base = node(%node_id) " \
                 f"MATCH path = (base)--(connected)--(similar:{model_cls.NAME}) " \
                 f"RETURN similar, count(connected) " \
                 f"ORDER BY count(connected) DESC "

        node_id = ModelService.get_model(
            model_cls,
            name=name
        ).id

        return ModelService.get_cyphered_list(
            model_cls,
            cypher.replace(cypher_placeholder, str(node_id)),
            start,
            limit
        )

    @staticmethod
    def create_model(model_cls: type, **kwargs) -> BaseModel:
        model_types = {
            Entity: ModelService._create_entity,
            Company: ModelService._create_entity,
            Genre: ModelService._create_entity,
            Category: ModelService._create_entity,
            Content: ModelService._create_content,
            DLC: ModelService._create_content,
            Game: ModelService._create_game,
        }
        method = model_types.get(model_cls)
        if not method:
            raise NotImplementedError
        return model_types[model_cls](model_cls, **kwargs)

    @staticmethod
    def delete_model(model_cls: type, name: str) -> None:
        instance = model_cls.nodes.get_or_none(name=name)
        if instance:
            instance.delete()

    @staticmethod
    def _create_entity(model_cls: Entity, name: str, **kwargs) -> Entity:
        instance = model_cls.nodes.get_or_none(name=name)
        if not instance:
            instance = model_cls(
                name=name
            )
            instance.save()
        return instance

    @staticmethod
    def _create_content(
            model_cls: type,
            name: str, short_desc: str, long_desc: str, header_image: str,
            is_free: bool = False, images: List[str] = [], movies: [List] = [],
            publishers: List[str] = [], developers: List[str] = [], date=None,
            **kwargs
    ) -> Content:
        instance = model_cls.nodes.get_or_none(name=name)

        if date:
            try:
                date = datetime.strptime(date, model_cls.DATE_FORMAT)
            except ValueError:
                date = None

        if not instance:
            instance = model_cls(
                name=name,
                is_free=is_free,
                short_desc=short_desc,
                long_desc=long_desc,
                header_image=header_image,
                images=images,
                movies=movies,
                date=date
            )
            instance.save()

        for publisher_name in publishers:
            publisher = ModelService._create_entity(Company, publisher_name)
            instance.publishers.connect(publisher)

        for developer_name in developers:
            developer = ModelService._create_entity(Company, developer_name)
            instance.developers.connect(developer)

        return instance

    @staticmethod
    def _create_game(
            model_cls: type,
            genres: List[str] = [], categories: List[str] = [],
            **kwargs
    ) -> Game:
        instance = ModelService._create_content(
            model_cls=model_cls,
            **kwargs
        )

        for genre_name in genres:
            genre = ModelService._create_entity(Genre, genre_name)
            instance.genres.connect(genre)

        for category_name in categories:
            category = ModelService._create_entity(Category, category_name)
            instance.categories.connect(category)

        return instance
