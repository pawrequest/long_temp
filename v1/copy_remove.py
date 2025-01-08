import sys
from pathlib import Path
from typing import Literal

from pawlogger import get_loguru

from long_temporary.copy_rem_back import ItineriesFile, Itinery

CopyModeType = Literal["copy", "delete", "dry", "add_manifest", "remove_manifest"]

logger = get_loguru(level="DEBUG", log_file=Path("log_temp.log"))
SF_DATA = r"D:\GAMES\Starfield\Data"
SGLS = r"D:\GAMES\Mods\manual\archives\NAFSeduce_0_2"
TEST1 = r"D:\GAMES\Mods\manual\test\1"
TEST2 = r"D:\GAMES\Mods\manual\test\2"
TEST3 = r"D:\GAMES\Mods\manual\test\3"

COPY_MODE: CopyModeType = "delete"

SOURCE_PATH: Path | None = None
SOURCE_PATH: Path | None = Path(TEST1)
MANIFEST_FILE: Path = Path("../file_references.json")
TARGET_PATH = Path(TEST3)


def main():
    _changed: bool = False
    itin_file = ItineriesFile(MANIFEST_FILE)
    itinery: Itinery | None = itin_file.get_itinery(TARGET_PATH)
    scanned = scanin()

    if scanned:
        if not itinery or list(scanned.manifests)[0] not in itinery.manifests:
            itinery = Itinery.merge2(itinery, scanned)
            _changed = True

    if not itinery:
        logger.error("No Itinery found - scan a directory or load a file")
        sys.exit(0)

    if COPY_MODE == "dry":
        logger.info(f"Merged Itinery:\n{itinery}")
        sys.exit(0)

    elif COPY_MODE in ["add_manifest", "copy"]:
        if itin_file.add_itin(itinery):
            _changed = True
        if COPY_MODE == "copy":
            itinery.copy_files()

    elif COPY_MODE in ["remove_manifest", "delete"]:
        _changed = bool(itin_file.pop_itin(itinery.target))
        if COPY_MODE == "delete":
            rem_result = itinery.remove_files()
            logger.info(rem_result.log_str)


    if _changed:
        itin_file.save_json()


def scanin() -> Itinery | None:
    scanned: Itinery | None = None
    if SOURCE_PATH:
        scanned = Itinery.from_scan(SOURCE_PATH, TARGET_PATH)
        logger.info(f"Scanned Itinery {scanned.multi_log_str(scanned)}")
    return scanned


if __name__ == "__main__":
    main()
