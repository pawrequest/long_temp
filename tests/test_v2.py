import pytest
from datetime import datetime, timedelta
from pathlib import Path
from long_temporary.mainfest import Manifest, scan_folder_sub_paths

@pytest.fixture
def temp_dir(tmp_path):
    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    (src / "file1.txt").write_text("data1")
    (src / "file2.txt").write_text("data2")
    (tgt / "file1.txt").write_text("data1")
    (tgt / "file2.txt").write_text("data2")
    (tgt / "file3.txt").write_text("data3")
    return src, tgt

def test_creates_manifest_from_scan(temp_dir):
    src, _ = temp_dir
    manifest = Manifest.from_scan(src)
    assert manifest.root == src
    assert {Path("file1.txt"), Path("file2.txt")} == set(map(Path, manifest.paths_relative))

def test_computes_tgt_sub_src_difference(temp_dir):
    src, tgt = temp_dir
    manifest = Manifest.tgt_sub_src(src, tgt)
    assert manifest.root == tgt
    assert set(map(Path, manifest.paths_relative)) == {Path("file3.txt")}

def test_adds_manifests_and_merges_paths():
    root = Path("root")
    m1 = Manifest(root=root, paths_relative={Path("a.txt")}, last_edit=datetime.now())
    m2 = Manifest(root=root, paths_relative={Path("b.txt")}, last_edit=datetime.now() - timedelta(days=1))
    m3 = m1 + m2
    assert m3.paths_relative == {Path("a.txt"), Path("b.txt")}
    assert m3.last_edit > m2.last_edit

def test_subtracts_manifests_and_removes_paths():
    root = Path("root")
    m1 = Manifest(root=root, paths_relative={Path("a.txt"), Path("b.txt")}, last_edit=datetime.now())
    m2 = Manifest(root=root, paths_relative={Path("b.txt")}, last_edit=datetime.now())
    m3 = m1 - m2
    assert m3.paths_relative == {Path("a.txt")}

def test_resolves_paths_relative_to_root():
    root = Path("/tmp/root")
    manifest = Manifest(root=root, paths_relative={Path("a.txt"), Path("b.txt")}, last_edit=datetime.now())
    resolved = manifest.paths_resolved()
    assert resolved == {root / "a.txt", root / "b.txt"}

def test_manifest_equality_and_hashing():
    root = Path("root")
    m1 = Manifest(root=root, paths_relative={Path("a.txt"), Path("b.txt")}, last_edit=datetime.now())
    m2 = Manifest(root=root, paths_relative={Path("a.txt"), Path("b.txt")}, last_edit=datetime.now())
    m3 = Manifest(root=root, paths_relative={Path("b.txt")}, last_edit=datetime.now())
    assert m1 == m2
    assert m1 != m3
    assert hash(m1) == hash(m2)
    assert hash(m1) != hash(m3)

def test_scan_folder_sub_paths_returns_relative_paths(tmp_path):
    d = tmp_path / "folder"
    d.mkdir()
    (d / "file.txt").write_text("abc")
    (d / "sub").mkdir()
    (d / "sub" / "file2.txt").write_text("def")
    paths = scan_folder_sub_paths(d)
    assert "file.txt" in paths
    assert "sub/file2.txt" in paths