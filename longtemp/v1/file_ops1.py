import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from longtemp.file_ops import CopyResult


@dataclass
class RemoveResult:
    files_removed: set[str] = field(default_factory=set)
    dirs_removed: set[str] = field(default_factory=set)
    missing_ignored: set[str] = field(default_factory=set)
    dirs_ignored: set[str] = field(default_factory=set)
    dirs_with_files: set[str] = field(default_factory=set)

    @property
    def log_str(self):
        return (
            f"Removed {len(self.files_removed)} files and {len(self.dirs_removed)} empty directories, "
            f"Ignored {len(self.missing_ignored)} Path/s (not found) and {len(self.dirs_ignored)} Directories (not empty)"
        )


def copy_overwrite_shutil(pathset: set[Path], source: Path, target: Path) -> CopyResult:
    copied = set()
    for path_ in pathset:
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
    return CopyResult(paths_processed=pathset, paths_success=copied)


def remove_files(pathset: set, tgt: Path, rem_res: RemoveResult = None) -> RemoveResult:
    rem_res = rem_res or RemoveResult()

    for tgt_path in pathset:
        dst_path = tgt / tgt_path
        if not dst_path.exists():
            rem_res.missing_ignored.add(str(dst_path))

        elif dst_path.is_file():
            rem_res.files_removed.add(str(dst_path))
            dst_path.unlink()

    return rem_res


def remove_empty_dirs(tgt: Path, rem_res: RemoveResult | None = None) -> RemoveResult:
    rem_res = rem_res or RemoveResult()
    for root, folders, filenames in os.walk(tgt, topdown=False):
        root_path = Path(root)
        for folder in folders:
            remove_empty_dirs(root_path / folder, rem_res)
        if filenames:
            rem_res.dirs_with_files.add(root)
        else:
            rem_res.dirs_removed.add(root)
            shutil.rmtree(root)

            # if not filenames and not dirnames:
            #     if Path(root).exists():
            #         rem_res.dirs_removed.add(root)
            #         shutil.rmtree(root)
            # else:
            #     rem_res.dirs_ignored.add(root)

    return rem_res


def remove_empty_dirs1(tgt, rem_res: RemoveResult | None = None) -> RemoveResult:
    rem_res = rem_res or RemoveResult()
    for root, dirnames, filenames in os.walk(tgt, topdown=False):
        for dir_ in dirnames:
            remove_empty_dirs(dir_, rem_res)
            if not filenames and not dirnames:
                if Path(root).exists():
                    rem_res.dirs_removed.add(root)
                    shutil.rmtree(root)
            else:
                rem_res.dirs_ignored.add(root)

    return rem_res


#
# def save_json(fp, data):
#     with open(fp, "w") as f:
#         # json.dump(data, f, indent=4)
#         json.dump(data, f, cls=DataclassEncoder, indent=4)
#         logger.info(f"Overwrote {fp}")
#
#
# def load_json(fp):
#     with open(fp, "r") as f:
#         return json.load(f)
#
#
# def update_json(fp, data):
#     try:
#         old_data = load_json(fp)
#         old_data.update(data)
#     except Exception as e:
#         logger.error(f"Error updating, creating new {fp}: {e}")
#         old_data = data
#     save_json(fp, old_data)
#     return old_data
#
#
# def append_json(fp, data):
#     old_data = load_json(fp)
#     old_data.append(data)
#     save_json(fp, old_data)
#     return old_data
