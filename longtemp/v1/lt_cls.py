from dataclasses import dataclass
from pathlib import Path

from longtemp.file_ops import FileOps
from longtemp.intinery_file import ItineriesFile
from longtemp.itinery import get_itinery
from longtemp.mainfest import Manifest


@dataclass
class LongTemp:
    json_path: Path
    itinery_file: ItineriesFile | None = None

    def __post_init__(self):
        self.itinery_file = self.itinery_file or ItineriesFile.from_json(self.json_path)

    def load_itinery(self, tgt: name):
        tgt = tgt or self.target
        file = self.itinery_file
        if itinery := get_itinery(tgt, file.itineries):
            logger.info(f"Loaded Itinery for {itinery}")
            self.itinery = self.itinery.merge_itinery(itinery)

    def add_scanned(self):
        if self.source and self.source.exists():
            manifest = Manifest.from_scan(self.source)
            self.itinery.add_manifest(manifest)

    def operate(self):
        file_operator = FileOps(self.itinery)
