import json


class Object:
    def to_json(self):
        """Returns a JSON serialized representation of the object."""
        return json.dumps(
            self.to_dict(), separators=(",", ":"), ensure_ascii=False
        )

    def to_dict(self):
        """Returns a dictionary representation of the object."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_json(cls, json_string):
        """Create an object from JSON serialized string."""
        return cls(**json.loads(json_string))

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        for attr in self.__dict__:
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True
