import json
from dataclasses import asdict, dataclass, field, is_dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Callable

from loguru import logger

from longtemp.itinery import Itinery, get_itinery


@dataclass
class ItineriesFile:
    itineries_json: Path
    itineries: list[Itinery] = field(default_factory=list)

    def __contains__(self, item):
        return item in self.itineries

    @classmethod
    def from_json(cls, itinery_file: Path):
        itineries = cls.load_json(itinery_file)
        return cls(itinery_file, itineries)

    def __str__(self):
        msg = f"'{self.itineries_json}': {len(self.itineries)} Itineri/es, {self.num_manifests()} source/s,  {self.num_paths_total()} path/s"
        return msg

    def num_paths_total(self):
        return sum([_.num_paths() for _ in self.itineries])

    def num_manifests(self):
        return sum([len(_.manifests) for _ in self.itineries])

    def long_str(self):
        if self.itineries:
            return str(self) + Itinery.multi_log_str(*self.itineries)


    @classmethod
    def load_json(cls, fp, converter: Callable | None = None):
        try:
            with open(fp, "r") as f:
                data = json.load(f, cls=DataClassDecoder)
                return converter(data) if converter else data
        except FileNotFoundError:
            logger.info(f"Itinery File not found at {fp}")
        except JSONDecodeError:
            logger.error(f"Error decoding itinery json file: {fp}")
        return converter() if converter else []

    def save_json(self):
        with open(self.itineries_json, "w") as f:
            json.dump(self.itineries, f, cls=DataclassEncoder, indent=4)
            logger.info(f"Updated: {self.long_str()}")

    def pop_itin_name(self, name:str):
        if existing_itin := get_itinery(name, self.itineries):
            logger.debug(f"Removing Itinery {name=}")
            self.itineries.remove(existing_itin)
            return existing_itin

    def update_itin(self, itin: Itinery):
        if exisiting := self.pop_itin_name(itin.name):
            logger.info(f"Merging new manifest into existing Itinery ({itin.name})")
            itin = exisiting.merge_itinery(itin)
        else:
            logger.debug(f"Added new {itin}")

        self.itineries.append(itin)
        return True

class DataClassDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        # if "source" in obj:
        #     return Manifest(**obj)
        # if "target" in obj:
        #     return Itinery(**obj)
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
