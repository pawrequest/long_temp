from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Self

from pydantic import BaseModel


class Manifest(BaseModel):
    """Record of a source directory and its files relative to the source"""

    root: Path
    paths_relative: set[Path] = field(default_factory=set)
    last_edit: datetime = field(default_factory=datetime.now)

    def paths_resolved(self):
        return {self.root / _ for _ in self.paths_relative}

    def __add__(self, other: Self):
        self.paths_relative = self.paths_relative.union(other.paths_relative)
        self.last_edit = datetime.now()
        return self

    def __sub__(self, other: Self):
        self.paths_relative = self.paths_relative - other.paths_relative
        self.last_edit = datetime.now()
        return self

    def __str__(self):
        return f"Manifest({self.root})"

    def __hash__(self):
        return hash(self.paths_relative)

    def __eq__(self, other: Self):
        return self.paths_relative == other.paths_relative

    @classmethod
    def from_scan(cls, root: Path) -> Self:
        return cls(root=root, paths_relative=scan_folder_sub_paths(root))


def scan_folder_sub_paths(root: Path) -> set[Path]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}
