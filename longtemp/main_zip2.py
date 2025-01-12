from pathlib import Path

from pawlogger import get_loguru

from longtemp.filetracker import FileTracker
from longtemp.itinery import Itinery
from longtemp.mainfest import Manifest
from longtemp.unrar import re_combine_archives, unpack_tmp

logger = get_loguru(level="DEBUG", log_file=Path("../data/log_temp.log"))

test_data = Path("../data/").resolve()
TEST1 = test_data / "1"
TEST2 = test_data / "2"
TEST3 = test_data / "3"
JSON_FILE = test_data / "file_references.json"
CYBERPUNK_DIR = Path(r"D:\GAMES\Cyberpunk 2077")
CYBERPUNK_DIR_BACKUP = Path(r"E:\SOFTWARE\GAMES\cyberpunk 2077\data dir bk\Cyberpunk 2077")
MODS = Path(r"D:\GAMES\Mods\cp77")
CORE_MODS = MODS / "framework"
DEPLOYED = MODS / "deployed"
DEV_MODS = MODS / "dev"

XMAS_MOD = Path(r"D:\GAMES\Mods\cp77\Cyber Xmas-11783-2-0-2-1735028378")
MY_MOD_DIR = Path(r"E:\prdev\repos\make_mod\src\make_mod\cyberScript\prDev")
MY_MOD_NAME = "prDev"
RANDOM_MOD_ARCHIVE = Path(r"D:\GAMES\Mods\cp77\NC Fashion Virtual Atelier-4805-9-0-l-1737218217.rar")


def leave_only_src_in_tgt(src: Path, tgt: Path):
    src_mani = Manifest.from_scan(src)
    tgt_manifest = Manifest.from_scan(tgt)
    to_remove = tgt_manifest.paths_relative - src_mani.paths_relative
    confirm = input(f"really remove {len(to_remove)} files not found in og_manifest? (y/n): ")
    if not confirm.lower().startswith("y"):
        return

    itin = Itinery.from_manifests([Manifest(paths_relative=to_remove, root=tgt)])
    itin.remove_files(tgt)


def remove_src_files_from_tgt(src: Path, tgt: Path, name: str = None):
    src_scan = Manifest.from_scan(src)
    tgt_scan = Manifest.from_scan(tgt)
    to_remove = tgt_scan.paths_relative.intersection(src_scan.paths_relative)
    remove_manifest = Manifest(paths_relative=to_remove, root=tgt)
    itin = Itinery.from_manifests([remove_manifest], name=name)
    return itin


def log_itinery(itin):
    tracker = FileTracker.from_json(JSON_FILE.resolve())
    tracker.update_itin(itin)
    tracker.save_json()


def redploy_archives(archives_dir, tgt):
    with unpack_tmp(archives_dir) as temp_dir:
        itin = Itinery.from_scan(temp_dir, name=str(archives_dir))
        itin.redeploy_files(tgt)
    return itin


if __name__ == "__main__":
    itin = redploy_archives(CORE_MODS, TEST3)
    # itin = redeploy_store_unpacked(CORE_MODS, TEST3, TEST2)
    log_itinery(itin)
    # itin = Itinery.from_scan(TEST1, name=str(TEST1))
    # itin.redeploy_files(TEST3, ignore_error=True)
    # log_itinery(itin)
