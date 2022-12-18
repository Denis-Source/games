import json

from neomodel import Relationship

from models.content import Content


class Game(Content):
    NAME = "Game"

    dlcs = Relationship("models.dlc.DLC", "DLC_OF")

    publishers = Relationship("models.company.Company", "PUBLISHED")
    developers = Relationship("models.company.Company", "DEVELOPED")

    genres = Relationship("models.genre.Genre", "GENRE_OF")
    categories = Relationship("models.category.Category", "CATEGORY_OF")

    def serialize_connections(self) -> dict:
        serialization = super().serialize_connections()
        serialization.update({
            "dlcs": [node.serialize() for node in self.dlcs],
        })
        return serialization
