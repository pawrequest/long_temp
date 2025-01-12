from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from longtemp.file_ops import RemoveResult, copy_overwrite_shutil, remove_files, remove_empty_dirs
from longtemp.itinery import Itinery


@dataclass
class FileOps:
    itinery: Itinery
    remove_result: RemoveResult = field(default_factory=RemoveResult)

    def do_copy(self, tgt: Path):
        cop_res = {}
        for manifest in self.itinery.manifests:
            copied = copy_overwrite_shutil(self.itinery.all_paths_relative(), manifest.source, tgt)
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

    def remove_files(self, tgt, rem_res: RemoveResult = None) -> RemoveResult:
        return remove_files(self.itinery.all_paths_relative(), tgt, rem_res)

    def remove_dirs(self, tgt, rem_res: RemoveResult = None) -> RemoveResult:
        return remove_empty_dirs(tgt, rem_res)
