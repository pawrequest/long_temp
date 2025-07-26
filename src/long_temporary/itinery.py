from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Self

from pydantic import BaseModel

from long_temporary.file_ops import FileopResult, copy_overwrite_shutil, delete_empty_folders, remove_files
from long_temporary.mainfest import Manifest

type MainfestDict = dict[str, Manifest]  # {str[root]: Manifest}

type FileOpRecords = dict[str, FileopResult]  # {datetime.iso: FileopResult}


class Itinery(BaseModel):
    """Record of a target directory and it's Manifests"""

    name: str
    manifests: MainfestDict = field(default_factory=dict)
    results: FileOpRecords | None = field(default_factory=dict)

    def copy_files(self, tgt: Path):
        for manifest in self.manifests.values():
            self._add_fileop(copy_overwrite_shutil(manifest.paths_relative, manifest.root, tgt))

    def remove_files(self, tgt: Path, result=None, ignore_errors=False):
        for manifest in self.manifests.values():
            self._add_fileop(remove_files(manifest.paths_relative, tgt, result=result, ignore_error=ignore_errors))

    def remove_empty_folders(self, tgt: Path):
        self._add_fileop(delete_empty_folders(tgt))

    def redeploy_files(self, tgt: Path, ignore_error=False):
        try:
            self.remove_files(tgt, ignore_errors=ignore_error)
            self.remove_empty_folders(tgt)
        except Exception as e:
            if not ignore_error:
                raise e
        self.copy_files(tgt)
        return self

    def _add_fileop(self, result: FileopResult):
        self.results[datetime.now().isoformat()] = result
        return self

    def update_manifest(self, manifest: Manifest):
        if existing_manifest := self.manifests.get(str(manifest.root)):
            manifest = manifest + existing_manifest
        self.manifests[str(manifest.root)] = manifest

    def __eq__(self, other):
        return self.manifests.values() == other.manifests.values()

    def __contains__(self, manifest: Manifest):
        return manifest in self.manifests.values()

    def __hash__(self):
        return hash([hash(_) for _ in self.manifests.values()])

    def __str__(self):
        return f"'{self.name}' -  {self.num_paths()} files from {len(self.manifests.values())} sources: ({[str(_) for _ in self.manifests.values()]})"

    def num_paths(self) -> int:
        return len(self.src_paths_relative())

    @classmethod
    def from_manifests(cls, *manifests: Manifest, name: str = None) -> Self:
        name = name or "__".join(_.root.name for _ in manifests)
        manifest_dict = {str(manifest.root): manifest for manifest in manifests}
        return cls(name=name, manifests=manifest_dict)

    # @classmethod
    # def from_scan(cls, src: Path, name: str = None):
    #     name = name or src.name
    #     return cls(name=name, manifests={str(src): Manifest.from_scan(src)})

    @classmethod
    def from_scans(cls, *srcs: Path, name: str = None) -> Self:
        manifests = [Manifest.from_scan(src) for src in srcs]
        return cls.from_manifests(*manifests, name=name)

    def src_paths_relative(self) -> set[Path]:
        return set.union(*[_.paths_relative for _ in self.manifests.values()]) if self.manifests else set()

    def src_paths_resolved(self):
        res = set.union({_.paths_resolved() for _ in self.manifests.values()})
        return res
