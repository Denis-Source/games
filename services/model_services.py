from datetime import datetime
from typing import List, Tuple, Type

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
    def get_model(model_cls: Type[Entity], **kwargs) -> Entity:
        instance = model_cls.nodes.get_or_none(**kwargs)
        if not instance:
            raise ModelNotFoundException
        return instance

    @staticmethod
    def get_filtered_list(
            model_cls: Type[Entity],
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
            model_cls: Type[Entity],
            cypher: str,
            start: int = 0,
            limit: int = None,
    ) -> Tuple[List[BaseModel], bool]:
        cypher += f"SKIP {start} LIMIT {limit}"
        results, _ = db.cypher_query(cypher)
        results = [model_cls.inflate(row[0]) for row in results]
        start += limit

        next_results, _ = db.cypher_query(cypher)
        return results, len(next_results) > 0

    @staticmethod
    def get_similar_list(
            model_cls: Type[Entity],
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
    def create_model(model_cls: Type[Entity], **kwargs) -> Entity:
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
    def delete_model(model_cls: Type[Entity], name: str) -> None:
        instance = model_cls.nodes.get_or_none(name=name)
        if instance:
            instance.delete()

    @staticmethod
    def _create_entity(model_cls: Type[Entity], name: str) -> Entity:
        instance = model_cls.nodes.get_or_none(name=name)
        if not instance:
            instance = model_cls(
                name=name
            )
            instance.save()
        return instance

    @staticmethod
    def _create_content(
            model_cls: Type[Entity],
            name: str, short_desc: str, long_desc: str, header_image: str,
            is_free: bool = False, images: List[str] = None, movies: [List] = None,
            publishers: List[str] = None, developers: List[str] = None, date=None,
    ) -> Content:
        if not images:
            images = []
        if not movies:
            movies = []
        if not publishers:
            publishers = []
        if not developers:
            developers = []

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
            model_cls: Type[Entity],
            genres: List[str] = None, categories: List[str] = None,
            **kwargs
    ) -> Game:
        instance = ModelService._create_content(
            model_cls=model_cls,
            **kwargs
        )

        if not genres:
            genres = []
        if not categories:
            categories = []

        for genre_name in genres:
            genre = ModelService._create_entity(Genre, genre_name)
            instance.genres.connect(genre)

        for category_name in categories:
            category = ModelService._create_entity(Category, category_name)
            instance.categories.connect(category)

        return instance
