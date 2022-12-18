from __future__ import annotations

from neomodel import StructuredNode, UniqueIdProperty, StringProperty

from models.base import BaseModel


class Entity(StructuredNode, BaseModel):
    NAME = "Entity"

    node_id = UniqueIdProperty(primary_key=True)
    name = StringProperty(unique_index=True)

    def __str__(self):
        return self.name

    def serialize(self, connections: bool = False) -> dict:
        serialization = {
            "name": self.name,
            "node_id": self.node_id
        }
        if connections:
            serialization.update({
                "connections": self.serialize_connections()
            })

        return serialization

    def serialize_connections(self) -> dict:
        return {}
