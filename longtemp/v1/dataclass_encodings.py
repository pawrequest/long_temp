import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


class DataClassDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        # if "source" in obj:
        #     return Manifest(**obj)
        # if "target" in obj:
        #     return Itinery(**obj)
        ...
        return obj


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, frozenset):
            return list(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)
