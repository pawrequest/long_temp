import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from longtemp.itinery import Itinery


@dataclass
class RemoveResult:
    files_removed: set[str] = field(default_factory=set)
    dirs_removed: set[str] = field(default_factory=set)
    missing_ignored: set[str] = field(default_factory=set)
    dirs_ignored: set[str] = field(default_factory=set)

    @property
    def log_str(self):
        return (
            f"Removed {len(self.files_removed)} files and {len(self.dirs_removed)} empty directories, "
            f"Ignored {len(self.missing_ignored)} Path/s (not found) and {len(self.dirs_ignored)} Directories (not empty)"
        )


@dataclass
class FileOps:
    itinery: Itinery
    remove_result: RemoveResult = field(default_factory=RemoveResult)


    def do_copy(self):
        cop_res = {}
        for manifest in self.itinery.manifests:
            copied = copy_files(self.itinery.all_paths_relative, manifest.source, self.itinery.target)
            cop_res[manifest.source] = copied
        logger.info(f"Copied {len(cop_res)} Manifests")
        logger.debug(cop_res)

    def do_remove(self) -> RemoveResult:
        rem_res = RemoveResult()
        rem_res = self.remove_files(rem_res)
        rem_res = self.remove_dirs(rem_res)
        logger.info(rem_res.log_str)
        self.remove_result = rem_res
        return rem_res

    def remove_files(self, rem_res: RemoveResult = None) -> RemoveResult:
        return remove_files(self.itinery.all_paths_relative, self.itinery.target, rem_res)

    def remove_dirs(self, rem_res: RemoveResult = None) -> RemoveResult:
        return remove_empty_dirs(self.itinery.target, rem_res)


def copy_files(pathlist: frozenset[Path], source: Path, target: Path) -> set[Path]:
    copied = set()
    for path_ in pathlist:
        try:
            src_path = source / path_
            dst_path = target / path_
            if src_path.is_dir():
                dst_path.mkdir(parents=True, exist_ok=True)
            elif src_path.is_file():
                if not dst_path.parent.exists():
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                copied.add(shutil.copy2(src_path, dst_path))
        except Exception as e:
            logger.error(f"Error copying {path_}: {e}")
            raise
    return copied


def remove_files(pathset: frozenset, tgt: Path, rem_res: RemoveResult = None) -> RemoveResult:
    rem_res = rem_res or RemoveResult()

    for tgt_path in pathset:
        dst_path = tgt / tgt_path
        if not dst_path.exists():
            rem_res.missing_ignored.add(str(dst_path))

        elif dst_path.is_file():
            rem_res.files_removed.add(str(dst_path))
            dst_path.unlink()

    return rem_res


def remove_empty_dirs(tgt, rem_res: RemoveResult | None = None) -> RemoveResult:
    rem_res = rem_res or RemoveResult()
    for root, dirnames, filenames in os.walk(tgt, topdown=False):
        for dir_ in dirnames:
            remove_empty_dirs(dir_)
            if not filenames:
                rem_res.dirs_removed.update(root)
                shutil.rmtree(root)
            else:
                rem_res.dirs_ignored.update(root)

    return rem_res

