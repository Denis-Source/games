from __future__ import annotations

from abc import abstractmethod


class BaseModel:
    NAME = "BaseModel"
    DATE_FORMAT = "%d %b, %Y"

    @abstractmethod
    def serialize(self, connections: bool = False) -> dict:
        raise NotImplementedError

    @abstractmethod
    def serialize_connections(self) -> dict:
        raise NotImplementedError

