import contextlib
import subprocess
import tempfile
from os import mkdir
from pathlib import Path
from shutil import rmtree

from loguru import logger

WINRAR = r"C:\Program Files\WinRAR\WinRAR.exe"
ARCHIVE_EXTS = [".zip", ".tar", ".tar.gz", "rar", ".7z"]


def unrar(archive: Path, output: Path, command="x", winrar: Path = WINRAR):
    args = [winrar, command, "-y", archive.resolve(), output]

    if not output.exists():
        output.mkdir(parents=True, exist_ok=True)
    logger.info(f"{archive} to {output}", category="Unpacking")
    subprocess.run(args)


def unpack_archives(scr: Path, tgt: Path):
    for path in scr.rglob("*"):
        if path.suffix in ARCHIVE_EXTS:
            unrar(path, tgt)



def re_combine_archives(archives_dir: Path, tgt_dir: Path):
    tgt_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Redeploying archives", category="Setup")
    unpack_archives(archives_dir, tgt_dir)


@contextlib.contextmanager
def unpack_tmp(archives_dir: Path):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        re_combine_archives(archives_dir, temp_dir)
        yield temp_dir
