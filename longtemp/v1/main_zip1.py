from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pawlogger import get_loguru

from longtemp.intinery_file import ItineriesFile
# from longtemp.itinery import Itinery
from longtemp.file_ops import FileOps, update_json
from longtemp.itinery import get_itinery
from longtemp.mainfest import Manifest
from longtemp.unrar import unrar

ARCHIVE_EXTS = [".zip", ".tar", ".tar.gz", "rar"]

logger = get_loguru(level="DEBUG", log_file=Path("../../data/log_temp.log"))

TEST1 = r"C:\prdev\tools\long_temporary\data\1"
TEST2 = r"C:\prdev\tools\long_temporary\data\2"
TEST3 = r"C:\prdev\tools\long_temporary\data\3"
TEST_ZIP = r"C:\prdev\tools\long_temporary\data\1\ns.zip"


CopyModeType = Literal["copy", "delete", "dry", "add_manifest", "remove_manifest", "remove_itinery"]
# COPY_MODE: CopyModeType = "delete"

# SOURCE_PATH: Path | None = Path(TEST_ZIP)
TARGET_TEST = Path(TEST3)
JSON_FILE: Path = Path("../../data/file_references.json")


def main(
    source: Path,
    target: Path,
    copy_mode: CopyModeType = "dry",
    itinery_path: Path = JSON_FILE,
):
    itin_file, itinery = itin_and_file(itinery_path, target)
    file_operator = FileOps(itinery)

    if copy_mode == "dry":
        logger.info(f"Merged Itinery:\n{itinery}")
        return itinery

    elif copy_mode in ["add_manifest", "copy"]:
        if source and source.exists():
            if source.suffix in ARCHIVE_EXTS:
                source = unpack(source)

            scan_src(itinery, source, target)

        if itin_file.add_itin(itinery):
            itinery.changes_made = True
        if copy_mode == "copy":
            file_operator.do_copy()

    elif copy_mode in ["remove_manifest", "remove_itinery", "delete"]:
        if source.suffix in ARCHIVE_EXTS:
            maybe_source = get_archive_dir(source)
            source = maybe_source if maybe_source.exists() else unpack(source)

        if copy_mode == "remove_manifest":
            itinery.changes_made = bool(itinery.remove_source(source))
            if itinery.is_empty():
                logger.info(f"Removing Empty Itinery {itinery.target}")
                itin_file.pop_target(itinery.target)
        elif copy_mode == "remove_itinery":
            removed_itin = itin_file.pop_target(itinery.target)
            itinery.changes_made = bool(removed_itin)
        elif copy_mode == "delete":
            file_operator.do_remove()
            removed_itin = itin_file.pop_target(itinery.target)
            itinery.changes_made = bool(removed_itin)

    if itinery.changes_made:
        itin_file.save_json()


def itin_and_file(itinery_path, target):
    itin_file = ItineriesFile(itinery_path)
    if itinery := get_itinery(target, itin_file.itineries):
        logger.info(f"Loaded Itinery for {itinery}")
    else:
        itinery = Itinery(target)
    return itin_file, itinery


def unpack(archive):
    unpacked = get_archive_dir(archive)
    unpacked.mkdir(parents=True, exist_ok=True)
    unrar(archive, unpacked)
    return unpacked


def get_archive_dir(source):
    unpacked = source.parent.parent / "unrarred" / (source.stem + "_" + source.suffix.split(".")[1])
    return unpacked


def scan_src(itinery, source, target):
    if scanned := Itinery.from_scan(source, target):
        scanned_mani = list(scanned.manifests)[0]
        if itinery and scanned_mani in itinery:
            logger.info(f"Manifest already in Itinery ({scanned_mani.source=} in {itinery.target=})")
        else:
            logger.info(f"Scanned new Itinery {scanned}")
            itinery.merge_itinery(scanned)
            itinery.changes_made = True

@dataclass
class ManiRecord:
    name: str
    manifest: Manifest

if __name__ == "__main__":
    deploy_dir = Path(r"D:\GAMES\Mods\archives\cyberpunk\deploy")
    cyberpunk_dir = Path(r"D:\GAMES\Cyberpunk 2077")
    cyberpunk_mods = Path(r"D:\GAMES\Mods\cp77") / "stage"
    # main(cyberpunk_dir, cyberpunk_dir, "add_manifest")

    test1 = Path(r'D:\GAMES\Mods\cp77\test\ApartmentDancers-10793-1-0-0-beta-2-1699475747')
    test2 = Path(r'D:\GAMES\Mods\cp77\test\Californication-7833-2-3-0-1716730835')

    mani = Manifest.from_scan(test2)

    itin = Itinery
    # record = ManiRecord("cyberpunk", mani)
    # save_json(JSON_FILE, mani)
    update_json(JSON_FILE, record)
    ...

    # archive_paths = [Path(_) for _ in deploy_dir.rglob("*") if _.suffix in ARCHIVE_EXTS]
    # for archive_path in archive_paths:
    #     main(archive_path, cyberpunk_dir, "delete")
    # anarch = Path(r"D:\GAMES\Mods\archives\cyberpunk\deploy\und.zip")
    # main(anarch, TARGET_TEST, "copy")
