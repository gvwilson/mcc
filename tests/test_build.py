"""Tests for build functionality."""

import pytest
from pathlib import Path
from pyfakefs.pytest_plugin import fs

from mccole.build import _copy_others

# Directories (using non-defaults to improve testing).
SRC = Path("/source")
DST = Path("/dest")


@pytest.fixture
def setup_files(fs):
    """Set up test files and directories in the fake filesystem."""
    fs.create_dir(str(SRC))
    fs.create_dir(str(DST))

    files = []
    files.append(fs.create_file(str(SRC / "file1.txt"), contents="file1 content"))
    fs.create_dir(str(SRC / "A"))
    files.append(fs.create_file(str(SRC / "A" / "file2.txt"), contents="file2 content"))
    fs.create_dir(str(SRC / "A" / "B"))
    files.append(fs.create_file(str(SRC / "A" / "B" / "file3.txt"), contents="file3 content"))
    files = [f.path for f in files]

    # Config uses strings for compatibility
    config = {
        "src": SRC,
        "dst": DST,
        "verbose": False
    }
    
    return {"files": files, "config": config}


def test_copy_others_preserves_structure(setup_files):
    """Test that files are copied with their directory structure preserved."""
    _copy_others(setup_files["config"], setup_files["files"])
    assert (DST / "file1.txt").exists()
    assert (DST / "A" / "file2.txt").exists()
    assert (DST / "A" / "B" / "file3.txt").exists()


def test_copy_others_preserves_content(setup_files):
    """Test that file content is preserved when copying."""
    _copy_others(setup_files["config"], setup_files["files"])
    assert (DST / "file1.txt").read_text() == "file1 content"
    assert (DST / "A" / "file2.txt").read_text() == "file2 content"
    assert (DST / "A" / "B" / "file3.txt").read_text() == "file3 content"


def test_copy_others_creates_directories(fs, setup_files):
    """Test that directories are created as needed."""
    fs.remove_object(str(DST))
    _copy_others(setup_files["config"], setup_files["files"])
    assert DST.exists()
    assert (DST / "A").exists()
    assert (DST / "A" / "B").exists()


def test_copy_others_with_empty_list(setup_files):
    """Test that function works correctly with an empty file list."""
    _copy_others(setup_files["config"], [])
    assert len(list(DST.iterdir())) == 0


def test_copy_others_verbose_output(setup_files, capsys):
    """Test that verbose output is generated when verbose=True."""
    setup_files["config"]["verbose"] = True
    _copy_others(setup_files["config"], setup_files["files"])
    captured = capsys.readouterr()
    assert "Copied file1.txt" in captured.out
    assert "Copied A/file2.txt" in captured.out
    assert "Copied A/B/file3.txt" in captured.out
