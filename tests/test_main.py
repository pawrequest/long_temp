import pytest

from longtemp.main import main
from longtemp.intinery_file import ItineriesFile


@pytest.fixture(scope="function")
def setup_env(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "file1.txt").write_text("content1")
    (source / "file2.txt").write_text("content2")
    yield source, target, tmp_path / "file_references.json"


def test_copy_files(setup_env):
    source, target, itinery_file = setup_env
    main(source=source, target=target, copy_mode="copy", itinery_path=itinery_file)
    assert (target / "file1.txt").exists()
    assert (target / "file2.txt").exists()
    assert itinery_file.exists()
    itin_file = ItineriesFile(itinery_file)
    assert itin_file.get_target(target) is not None


def test_dry_run_does_not_copy_files(setup_env):
    source, target, itinery_file = setup_env
    main(source=source, target=target, copy_mode="dry", itinery_path=itinery_file)
    assert not (target / "file1.txt").exists()
    assert not (target / "file2.txt").exists()


def test_add_manifest_to_itinery(setup_env):
    source, target, itinery_file = setup_env
    main(source=source, target=target, itinery_path=itinery_file, copy_mode="add_manifest")
    itinery = ItineriesFile(itinery_file).get_target(target)
    assert itinery is not None
    assert len(itinery.manifests) == 1


def test_remove_manifest_from_itinery(setup_env):
    source, target, itinery_file = setup_env
    main(source=source, target=target, copy_mode="add_manifest", itinery_path=itinery_file)
    main(source=source, target=target, copy_mode="remove_manifest", itinery_path=itinery_file)
    itinery = ItineriesFile(itinery_file).get_target(target)
    assert itinery is None


def test_delete_files_from_target(setup_env):
    source, target, itinery_file = setup_env

    main(source=source, target=target, copy_mode="copy", itinery_path=itinery_file)
    assert (target / "file1.txt").exists()

    main(source=source, target=target, copy_mode="delete", itinery_path=itinery_file)
    assert not (target / "file1.txt").exists()
