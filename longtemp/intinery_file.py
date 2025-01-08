import json
from dataclasses import asdict, dataclass, field, is_dataclass
from json import JSONDecodeError
from pathlib import Path

from loguru import logger

from longtemp.itinery import Itinery, Manifest, get_itinery


@dataclass
class ItineriesFile:
    itinery_file: Path
    itineries: list[Itinery] = field(default_factory=list)

    def __str__(self):
        msg = f"'{self.itinery_file}': {len(self.itineries)} Itineri/es, {self.num_manifests()} source/s,  {self.num_paths_total()} path/s"
        return msg

    def num_paths_total(self):
        return sum([_.num_paths() for _ in self.itineries])

    def num_manifests(self):
        return sum([len(_.manifests) for _ in self.itineries])

    def long_str(self):
        if self.itineries:
            return str(self) + Itinery.multi_log_str(*self.itineries)

    def __post_init__(self):
        self.itineries = self.load_json()
        if self.itineries:
            logger.info(f"Loaded {self}")

    def load_json[T: type | None](self, as_type: T = None) -> list[T]:
        try:
            with open(self.itinery_file, "r") as f:
                data = json.load(f, cls=self.DataClassDecoder)
                return as_type(data) if as_type else data
        except FileNotFoundError:
            logger.info(f"Itinery File not found at {self.itinery_file}")
        except JSONDecodeError:
            logger.error(f"Error decoding itinery file: {self.itinery_file}")
        return as_type() if as_type else []

    def save_json(self):
        with open(self.itinery_file, "w") as f:
            json.dump(self.itineries, f, cls=self.DataclassEncoder, indent=4)
            logger.info(f"Updated: {self.long_str()}")

    def get_target(self, tgt: Path):
        return get_itinery(tgt, self.itineries)

    def pop_target(self, tgt: Path):
        if existing_itin := self.get_target(tgt):
            logger.debug(f"Removing Itinery {tgt=}")
            self.itineries.remove(existing_itin)
            return existing_itin

    def add_itin(self, itin: Itinery):
        if itin in self.itineries:
            # logger.debug(f"Itinery {itin.target} already in list")
            return False

        if exisiting := self.pop_target(itin.target):
            logger.info(f"Merging new manifest into existing Itinery ({itin.target})")
            itin = exisiting.merge_itinery(itin)
        else:
            logger.debug(f"Added new {itin}")

        self.itineries.append(itin)
        return True

    class DataClassDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            super().__init__(object_hook=self.object_hook, *args, **kwargs)

        def object_hook(self, obj):
            if "source" in obj:
                return Manifest(**obj)
            if "target" in obj:
                return Itinery(**obj)
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
