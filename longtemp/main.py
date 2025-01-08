from pathlib import Path
from typing import Literal

from pawlogger import get_loguru

from longtemp.file_ops import FileOps
from longtemp.intinery_file import ItineriesFile
from longtemp.itinery import Itinery

logger = get_loguru(level="DEBUG", log_file=Path("../data/log_temp.log"))

TEST1 = r"C:\prdev\tools\long_temporary\data\1"
TEST2 = r"C:\prdev\tools\long_temporary\data\2"
TEST3 = r"C:\prdev\tools\long_temporary\data\3"

CopyModeType = Literal["copy", "delete", "dry", "add_manifest", "remove_manifest", "remove_itinery"]
COPY_MODE: CopyModeType = "delete"

SOURCE_PATH: Path | None = Path(TEST1)
TARGET_PATH = Path(TEST3)
JSON_FILE: Path = Path("../data/file_references.json")


def main(
    source: Path | None = SOURCE_PATH,
    target: Path | None = TARGET_PATH,
    copy_mode: CopyModeType = COPY_MODE,
    itinery_path: Path = JSON_FILE,
):
    _changed: bool = False
    itin_file = ItineriesFile(itinery_path)

    if itinery := itin_file.get_target(target):
        logger.info(f"Loaded Itinery for {itinery}")
    else:
        itinery = Itinery(target)
        logger.info(f"Created new Itinery {itinery}")

    file_operator = FileOps(itinery)

    if copy_mode == "dry":
        logger.info(f"Merged Itinery:\n{itinery}")
        return itinery

    elif copy_mode in ["add_manifest", "copy"]:
        if source and source.exists():
            if scanned := Itinery.from_scan(source, target):
                scanned_mani = list(scanned.manifests)[0]
                if itinery and scanned_mani in itinery:
                    logger.info(f"Manifest already in Itinery ({scanned_mani.source=} in {itinery.target=})")
                else:
                    logger.info(f"Scanned new Itinery {scanned}")
                    itinery.merge_itinery(scanned)
                    itinery.changes_made = True

        if itin_file.add_itin(itinery):
            itinery.changes_made = True
        if copy_mode == "copy":
            file_operator.do_copy()

    elif copy_mode in ["remove_manifest", "remove_itinery", "delete"]:
        if copy_mode == "remove_manifest":
            itinery.changes_made = bool(itinery.remove_source(source))
            if itinery.is_empty():
                logger.info(f"Removing Empty Itinery {itinery.target}")
                itin_file.pop_target(itinery.target)
        elif copy_mode == "remove_itinery":
            itinery.changes_made = bool(itin_file.pop_target(itinery.target))
        elif copy_mode == "delete":
            file_operator.do_remove()
            itinery.changes_made = bool(itin_file.pop_target(itinery.target))

    if itinery.changes_made:
        itin_file.save_json()


if __name__ == "__main__":
    main()
