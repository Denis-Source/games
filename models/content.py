from neomodel import BooleanProperty, StringProperty, DateProperty, ArrayProperty, Relationship

from models.entity import Entity


class Content(Entity):
    NAME = "Content"

    is_free = BooleanProperty(required=True)
    short_desc = StringProperty(required=True)
    long_desc = StringProperty(required=True)
    date = DateProperty()

    header_image = StringProperty(required=True)
    images = ArrayProperty()
    movies = ArrayProperty()

    publishers = Relationship("models.company.Company", "PUBLISHED")
    developers = Relationship("models.company.Company", "DEVELOPED")

    def serialize(self, connections: bool = False) -> dict:
        serialization = super().serialize(connections=connections)

        if self.date:
            formatted_date = self.date.strftime(self.DATE_FORMAT)
        else:
            formatted_date = None

        serialization.update({
            "is_free": self.is_free,
            "long_desc": self.long_desc,
            "short_desc": self.short_desc,
            "date": formatted_date,
            "header_image": self.header_image,
            "images": self.images,
            "movies": self.movies,
        })
        return serialization

    def serialize_connections(self) -> dict:
        return {
            "genres": [node.serialize() for node in self.genres],
            "categories": [node.serialize() for node in self.categories],

            "developers": [node.serialize() for node in self.developers],
            "publishers": [node.serialize() for node in self.publishers],
        }
