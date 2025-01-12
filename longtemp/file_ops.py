import os
import shutil
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel

OpType = Literal["copy", "delete", "replace", "prune_empty_folders"]


class FileopResult(BaseModel):
    file_op: OpType
    root: Path | None = None
    paths_processed: set[Path] = field(default_factory=set)
    files_copied: set[Path] = field(default_factory=set)
    files_deleted: set[Path] = field(default_factory=set)
    folders_created: set[Path] = field(default_factory=set)
    folders_deleted: set[Path] = field(default_factory=set)
    paths_failed: set[Path] = field(default_factory=set)
    paths_skipped: set[Path] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)


def copy_overwrite_shutil(
    rel_paths: set[Path], root: Path, target: Path, result: FileopResult = None, ignore_error=False
) -> FileopResult:
    result = result or FileopResult(file_op="copy", root=root)
    for rel_path in rel_paths:
        try:
            src_path = root / rel_path
            dst_path = target / rel_path
            result.paths_processed.add(rel_path)
            if src_path.is_dir():
                dst_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Making folder: {dst_path}", category="Copying")
                result.folders_created.add(dst_path)
            elif src_path.is_file():
                # if not dst_path.parent.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                result.files_copied.add(shutil.copy2(src_path, dst_path))
                logger.debug(f"Copying file: {dst_path}", category="Copying")
        except OSError as e:
            logger.error(f"Error copying {rel_path}: {e}")
            result.paths_failed.add(root / rel_path)
            if not ignore_error:
                raise e
    return result


def remove_files(rel_paths: set, root: Path, result: FileopResult = None, ignore_error=False) -> FileopResult:
    result = result or FileopResult(file_op="delete", root=root)
    for rel_path in rel_paths:
        result.paths_processed.add(rel_path.resolve())
        try:
            dst_path = root.resolve() / rel_path
            logger.debug(f"Removing file: {dst_path}", category="Removing")
            if dst_path.is_file():
                dst_path.unlink()
                result.files_deleted.add(dst_path)  #
        except Exception as e:
            logger.error(f"Error removing {root / rel_path}")
            result.paths_failed.add(root / rel_path)
            if not ignore_error:
                raise e
    return result


def delete_empty_folders(root, result: FileopResult | None = None) -> FileopResult:
    result = result or FileopResult(file_op="prune_empty_folders", root=root)

    for current_dir, subdirs, files in os.walk(root, topdown=False):
        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in result.folders_deleted:
                still_has_subdirs = True
                break

        if not any(files) and not still_has_subdirs:
            logger.debug(f"Removing empty folder: {current_dir}", category="Removing")
            os.rmdir(current_dir)
            result.folders_deleted.add(current_dir)
        else:
            result.paths_skipped.add(current_dir)

    return result


class FileOp(BaseModel):
    result: FileopResult
    tgt: Path
    op_type: OpType
