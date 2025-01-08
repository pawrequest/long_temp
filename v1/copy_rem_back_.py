import dataclasses
import json
import os
import shutil
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Iterable, Self

from loguru import logger


def coerce(coerceable):
    for field_ in dataclasses.fields(coerceable):
        value = getattr(coerceable, field_.name)
        setattr(coerceable, field_.name, field_.type(value))


@dataclass
class Manifest:
    source: Path
    paths_relative: frozenset[Path] = field(default_factory=frozenset)
    creation_date: str = field(default_factory=datetime.now().isoformat)

    def __str__(self):
        return f"Manifest({self.source})"

    def __hash__(self):
        return hash(self.paths_relative)

    def __post_init__(self):
        coerce(self)

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
    target: Path
    manifests: frozenset[Manifest] = field(default_factory=frozenset)

    def __eq__(self, other):
        return self.manifests == other.manifests

    def __hash__(self):
        return hash([hash(_) for _ in self.manifests])

    def __str__(self):
        return f"target='{self.target}' | {self.num_files_meth()} files from {len(self.manifests)} sources: ({[str(_) for _ in self.manifests]})"

    def __post_init__(self):
        coerce(self)

    def num_files_meth(self):
        return len(self.all_paths_relative)

    @classmethod
    def multi_log_str(cls, *itins):
        msg = f": \n\t{'\n\t'.join(str(_) for _ in itins)}"
        return msg

    def __bool__(self):
        return bool(self.manifests)

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
        return frozenset.union(*[_.paths_relative for _ in self.manifests])

    def add_manifest(self, manifest: Manifest):
        if manifest in self.manifests:
            logger.debug("Manifest already in Itinerary - aborting Add")
        logger.info(f"Adding Manifest: {manifest.source} to {self.target}")
        self.manifests = self.manifests | {manifest}
        return self

    def copy_files(self):
        logger.info(f"Copying {self.num_files_meth()} paths to {self.target}")
        for manifest in self.manifests:
            for path_ in manifest.paths_relative:
                try:
                    src_path = manifest.source / path_
                    dst_path = self.target / path_
                    if src_path.is_dir():
                        dst_path.mkdir(parents=True, exist_ok=True)
                    elif src_path.is_file():
                        if not dst_path.parent.exists():
                            dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        # logger.info(f"Copied file: {src_path} to {dst_path}")
                except Exception as e:
                    logger.error(f"Error copying {path_}: {e}")
                    raise

    def remove_files(self, rem_res:RemoveResult = None) -> RemoveResult:
        rem_res = RemoveResult()

        for tgt_path in self.all_paths_relative:
            dst_path = self.target / tgt_path
            if not dst_path.exists():
                rem_res.missing.add(str(dst_path))

            elif dst_path.is_file():
                rem_res.files.add(str(dst_path))
                dst_path.unlink()

        empty, not_empty = remove_empty_dirs(self.target)
        rem_res.dirs.update(empty)
        rem_res.not_empty.update(not_empty)

        return rem_res

    # def remove_empty_dirs(
    #     self,
    #
    # ) -> tuple[set[str], set[str]]:
    #     empty = set()
    #     n_set = set()
    #     r_set = set()
    #     for root, dirnames, filenames in os.walk(self.target, topdown=False):
    #         r_set.add(root)
    #         for dir_ in dirnames if dirnames else []:
    #             self.remove_empty_dirs(dir_)
    #         else:
    #             empty.add(root)
    #             # os.rmdir(root)
    #             shutil.rmtree(root)
    #     res = empty, r_set - empty
    #     return res


@dataclass
class ItineriesFile:
    itinery_file: Path
    itineries: list[Itinery] = field(default_factory=list)

    def __str__(self):
        msg = f"ItineriesFile('{self.itinery_file}') with {len(self.itineries)} Itineries"
        if self.itineries:
            msg += Itinery.multi_log_str(*self.itineries)
        return msg

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
            logger.info(f"Updated: {str(self)}")

    def save_json2(self):
        with open(self.itinery_file, "r") as f:
            try:
                exist = json.load(f, cls=self.DataClassDecoder) if self.itinery_file.exists() else []
            except (JSONDecodeError, FileNotFoundError):
                exist = []

        to_update = [itinery for itinery in self.itineries if itinery not in exist]
        if to_update:
            with open(self.itinery_file, "w") as f:
                json.dump(to_update, f, cls=self.DataclassEncoder, indent=4)
                logger.info(f"Updated: {str(self)}")

    def get_itinery(self, tgt: Itinery | Path):
        return get_itinery(tgt, self.itineries)

    def pop_itin(self, tgt: Path):
        if existing_itin := self.get_itinery(tgt):
            logger.debug(f"Removing Itinery {tgt=}")
            self.itineries.remove(existing_itin)
            return existing_itin

    def add_itin(self, itin: Itinery):
        if itin in self.itineries:
            # logger.debug(f"Itinery {itin.target} already in list")
            return False

        if exisiting := self.pop_itin(itin.target):
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


@dataclass
class RemoveResult:
    files: set[str] = field(default_factory=set)
    dirs: set[str] = field(default_factory=set)
    missing: set[str] = field(default_factory=set)
    not_empty: set[str] = field(default_factory=set)

    @property
    def log_str(self):
        return (
            f"Removed {len(self.files)} files and {len(self.dirs)} empty directories, "
            f"Ignored {len(self.missing)} Path/s (not found) and {len(self.not_empty)} Directories (not empty)"
        )


def dir_empty(dir_path):
    try:
        next(os.scandir(dir_path))
        return False
    except StopIteration:
        return True


def dir_tree_empty(tree_root):
    for dirpath, dirnames, filenames in os.walk(tree_root):
        if filenames:
            return False
    return True


def get_itinery(tgt: Itinery | Path, itineries: Iterable[Itinery]):
    if isinstance(tgt, Itinery):
        tgt = tgt.target
    return next((_ for _ in itineries if _.target == tgt), None) if itineries else None


def all_sub_paths(folder: Path) -> list[Path]:
    file_list = []
    for path in folder.rglob("*"):
        file_list.append(path.relative_to(folder).as_posix())
    return file_list


def remove_empty_dirs(target: Path) -> tuple[set[str], set[str]]:
    empty = set()
    r_set = set()
    for root, dirnames, filenames in os.walk(target, topdown=False):
        r_set.add(root)
        for dir_ in dirnames:
            remove_empty_dirs(dir_)
        else:
            empty.add(root)
            shutil.rmtree(root)
    res = empty, r_set - empty
    return res

