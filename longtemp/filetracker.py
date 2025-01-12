import json
from dataclasses import field
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from longtemp.itinery import Itinery

type ItineryDict = dict[str, Itinery]  # {str[name]: Itinery}


class FileTracker(BaseModel):
    itineries_json: Path
    itineries: ItineryDict = field(default_factory=dict)

    def __getitem__(self, item):
        return self.itineries.get(item)

    def __setitem__(self, key, value):
        self.itineries[key] = value

    def __contains__(self, item: str):
        return item in self.itineries.keys() or item in self.itineries.values()

    @classmethod
    def from_json(cls, json_fp: Path):
        if not json_fp.exists() or not json_fp.is_file() or not json_fp.suffix == ".json":
            logger.warning(f"No Itineries found at {json_fp}")
            return cls(itineries_json=json_fp)

        with open(json_fp, "r") as f:
            data = json.load(f)

        ifile = cls(**data)
        logger.info(f"Loaded {len(ifile.itineries)} Itineries from {json_fp}", category="Logging")

        return ifile

    def save_json(self):
        with open(self.itineries_json, "w") as f:
            data = self.model_dump(mode="json")
            json.dump(data, f)
            logger.info(f"OverWrote: {str(data)}", category="Logging")

    def update_itin(self, itin: Itinery):
        if self.itineries.get(itin.name):
            logger.info(f"Merging Itineries ({itin.name})", category="Logging")
            for manifest in itin.manifests.values():
                self[itin.name].update_manifest(manifest)
        else:
            logger.debug(f"Added new Itinery {itin}")
            self.itineries[itin.name] = itin
        self.itineries = {k: v for k, v in sorted(self.itineries.items(), key=lambda x: x[1].name)}
