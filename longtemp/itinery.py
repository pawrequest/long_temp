import dataclasses
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Self

from loguru import logger


@dataclass
class Manifest:
    """Record of a source directory and its files relative to the source"""

    source: Path
    paths_relative: frozenset[Path] = field(default_factory=frozenset)
    creation_date: str = field(default_factory=datetime.now().isoformat)

    def __str__(self):
        return f"Manifest({self.source})"

    def __hash__(self):
        return hash(self.paths_relative)

    def __post_init__(self):
        coerce_dataclass(self)

    def __eq__(self, other: Self):
        return self.paths_relative == other.paths_relative

    @classmethod
    def from_scan(cls, source: Path) -> Self:
        file_list = all_sub_paths(source)
        return cls(source=source, paths_relative=frozenset(file_list))

    @property
    def paths_source(self) -> set[Path]:
        return {self.source / path for path in self.paths_relative}


@dataclass
class Itinery:
    """Record of a target directory and it's Manifests"""

    target: Path
    manifests: frozenset[Manifest] = field(default_factory=frozenset)
    changes_made: bool = False

    def __eq__(self, other):
        return self.manifests == other.manifests

    def __contains__(self, manifest: Manifest):
        return manifest in self.manifests

    def __hash__(self):
        return hash([hash(_) for _ in self.manifests])

    def __str__(self):
        return f"'{self.target}' -  {self.num_paths()} files from {len(self.manifests)} sources: ({[str(_) for _ in self.manifests]})"

    def __post_init__(self):
        coerce_dataclass(self)

    def num_paths(self) -> int:
        return len(self.all_paths_relative)

    @classmethod
    def multi_log_str(cls, *itins):
        msg = f": \n\t{'\n\t'.join(str(_) for _ in itins)}"
        return msg

    # def __bool__(self):
    #     return bool(self.manifests)

    @classmethod
    def merge2(cls, itin1: Self | None, itin2: Self | None) -> Self:
        if itin1 is None:
            return itin2
        elif itin2 is None:
            return itin1
        elif itin1.target != itin2.target:
            raise ValueError("Target MisMatch")
        # logger.info(f"Merging Itineries: {itin1.target} with {itin2.target}")
        [itin1.add_manifest(mani) for mani in itin2.manifests if mani not in itin1.manifests]
        return itin1

    @classmethod
    def from_scan(cls, src: Path, tgt: Path):
        return cls(target=tgt, manifests=frozenset([Manifest.from_scan(src)]))

    def merge_itinery(self, other: Self):
        return self.merge2(self, other)

    @property
    def all_paths_relative(self) -> frozenset[Path]:
        return frozenset.union(*[_.paths_relative for _ in self.manifests]) if self.manifests else frozenset()

    def add_manifest(self, manifest: Manifest):
        if manifest in self.manifests:
            logger.debug("Manifest already in Itinerary - aborting Add")
        logger.info(f"Adding Manifest: {manifest.source} to {self.target}")
        self.manifests = self.manifests | {manifest}
        return self

    def remove_manifest(self, manifest: Manifest):
        if manifest in self.manifests:
            logger.debug(f"Removing Manifest: {manifest.source} from {self.target}")
            self.manifests = self.manifests - {manifest}
        return self

    def remove_source(self, source: Path):
        self.manifests = frozenset([_ for _ in self.manifests if _.source != source])

        return self

    def is_empty(self):
        return len(self.manifests) == 0


def get_itinery(tgt: Itinery | Path, itineries: Iterable[Itinery]):
    if isinstance(tgt, Itinery):
        tgt = tgt.target
    return next((_ for _ in itineries if _.target == tgt), None) if itineries else None


def all_sub_paths(folder: Path) -> list[Path]:
    file_list = []
    for path in folder.rglob("*"):
        file_list.append(path.relative_to(folder).as_posix())
    return file_list


def coerce_dataclass(coerceable):
    for field_ in dataclasses.fields(coerceable):
        value = getattr(coerceable, field_.name)
        setattr(coerceable, field_.name, field_.type(value))
