from pathlib import Path

from pawlogger import get_loguru
from long_temporary.itinery import Itinery
from long_temporary.mainfest import Manifest
from long_temporary.unrar import unpack_tmp

logger = get_loguru(level='DEBUG', log_file=Path('../data/log_temp.log'))

test_data = Path('../data/').resolve()
TEST1 = test_data / '1'
TEST2 = test_data / '2'
TEST3 = test_data / '3'
JSON_FILE = test_data / 'file_references.json'


def leave_only_src_in_tgt(src: Path, tgt: Path):
    to_rem = Manifest.tgt_sub_src(src, tgt)
    confirm = input(
        f'really remove {len(to_rem)} files not found in og_manifest? (y/n): '
    )
    if not confirm.lower().startswith('y'):
        return None
    itin = Itinery.from_manifests(to_rem, name=to_rem.root.name)
    itin.remove_files(tgt)
    itin.remove_empty_folders(tgt)
    return itin


def remove_srcs_from_tgt(*srcs: Path, tgt: Path, name: str = None):
    itin = Itinery.from_manifests(*[Manifest.from_scan(src) for src in srcs], name=name)
    logger.debug(f"Removing files from target {tgt} that are not in sources: {srcs}")
    confirm = input(
        f'really remove {len(itin.manifests)} files not found in sources? (y/n): '
    )
    if not confirm.lower().startswith('y'):
        return None
    itin.remove_files(tgt)
    itin.remove_empty_folders(tgt)
    return itin


def redeploy_archives(archives_dir, tgt, ignore_error=False):
    with unpack_tmp(archives_dir) as temp_dir:
        itin = Itinery.from_scans(temp_dir, name=archives_dir.name)
        itin.redeploy_files(tgt, ignore_error=ignore_error)
    return itin


def redeploy_folder(src: Path, tgt: Path, ignore_error=False):
    itin = Itinery.from_scans(src)
    itin.redeploy_files(tgt, ignore_error=ignore_error)
    return itin
