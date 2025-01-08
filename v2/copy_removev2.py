import sys
from pathlib import Path
from typing import Literal

from pawlogger import get_loguru

from long_temporary.v2.file_ops_cls import FileOps
from long_temporary.v2.intinery_file import ItineriesFile
from long_temporary.v2.itinery import Itinery

CopyModeType = Literal["copy", "delete", "dry", "add_manifest", "remove_manifest", "remove_itinery"]

logger = get_loguru(level="DEBUG", log_file=Path("log_temp.log"))

TEST1 = r"C:\prdev\tools\long_temporary\data\1"
TEST2 = r"C:\prdev\tools\long_temporary\data\2"
TEST3 = r"C:\prdev\tools\long_temporary\data\3"

COPY_MODE: CopyModeType = "delete"

SOURCE_PATH: Path | None = None
SOURCE_PATH: Path | None = Path(TEST1)
TARGET_PATH = Path(TEST3)

MANIFEST_FILE: Path = Path("file_references.json")


def main():
    _changed: bool = False
    itin_file = ItineriesFile(MANIFEST_FILE)

    if itinery := itin_file.get_target(TARGET_PATH):
        logger.info(f"Loaded Itinery for {itinery}")

    if SOURCE_PATH and SOURCE_PATH.exists():
        if scanned := Itinery.from_scan(SOURCE_PATH, TARGET_PATH):
            scanned_mani = list(scanned.manifests)[0]
            if itinery and scanned_mani in itinery:
                logger.info(f"Manifest already in Itinery ({scanned_mani.source=} in {itinery.target=})")
                _changed = False
            else:
                logger.info(f"Scanned new Itinery {scanned}")
                itinery = Itinery.merge2(itinery, scanned)
                _changed = True

    if not itinery:
        logger.error("No Itinery found - scan a directory or load a file")
        sys.exit(0)

    file_operator = FileOps(itinery)

    if COPY_MODE == "dry":
        logger.info(f"Merged Itinery:\n{itinery}")
        sys.exit(0)

    elif COPY_MODE in ["add_manifest", "copy"]:
        if itin_file.add_itin(itinery):
            _changed = True
        if COPY_MODE == "copy":
            file_operator.do_copy()

    elif COPY_MODE in ["remove_manifest", "remove_itinery", "delete"]:
        if COPY_MODE == "remove_manifest":
            _changed = itinery.remove_source(SOURCE_PATH)
        elif COPY_MODE == "remove_itinery":
            _changed = itin_file.pop_target(itinery.target)
        elif COPY_MODE == "delete":
            file_operator.do_remove()
            _changed = itin_file.pop_target(itinery.target)

    if bool(_changed):
        itin_file.save_json()


def scanin() -> Itinery | None:
    if SOURCE_PATH:
        scanned = Itinery.from_scan(SOURCE_PATH, TARGET_PATH)
        logger.info(f"Scanned Itinery {scanned.multi_log_str(scanned)}")
        return scanned


if __name__ == "__main__":
    main()
