import json


class Object:
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)

    def to_json(self, exclude_none=True):
        return json.dumps(
            self.to_dict(exclude_none), ensure_ascii=False, separators=(",", ":")
        ).replace("/", r"\/")

    def to_dict(self, exclude_none=True, recursive=True):
        data = {}
        for k, v in self.__dict__.items():
            if v is None and exclude_none:
                continue
            if recursive and isinstance(v, Object):
                data[k] = v.to_dict(exclude_none, recursive)
            else:
                data[k] = v
        return data
