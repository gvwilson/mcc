"""Tests for build functionality."""

from pathlib import Path
import pytest

from mccole.build import _copy_others, _convert_markdowns

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
    files.append(
        fs.create_file(str(SRC / "A" / "B" / "file3.txt"), contents="file3 content")
    )
    files = [f.path for f in files]

    # Config uses strings for compatibility
    config = {"src": SRC, "dst": DST, "verbose": False}

    return {"files": files, "config": config}


@pytest.fixture
def setup_markdown_files(fs):
    """Set up test Markdown files and directories in the fake filesystem."""
    fs.create_dir(str(SRC))
    fs.create_dir(str(DST))

    files = []
    files.append(
        fs.create_file(
            str(SRC / "index.md"),
            contents="# Title\n\nSome content.\n[Link to root](@root/index.html)",
        )
    )
    fs.create_dir(str(SRC / "docs"))
    files.append(
        fs.create_file(
            str(SRC / "docs" / "page.md"),
            contents="## Subtitle\n\n- List item 1\n- List item 2\n<img src='@root/images/logo.png'>",
        )
    )
    fs.create_dir(str(SRC / "docs" / "subdir"))
    files.append(
        fs.create_file(
            str(SRC / "docs" / "subdir" / "deep.md"),
            contents="### Deep page\n\n[Back to home](@root/index.html)\n[To page](@root/docs/page.html)",
        )
    )
    files = [f.path for f in files]

    # Config uses strings for compatibility
    config = {"src": SRC, "dst": DST, "verbose": False}

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


def test_convert_markdowns_preserves_structure(setup_markdown_files):
    """Test that markdown files are converted with directory structure preserved."""
    _convert_markdowns(setup_markdown_files["config"], setup_markdown_files["files"])
    assert (DST / "index.html").exists()
    assert (DST / "docs" / "page.html").exists()


def test_convert_markdowns_converts_content(setup_markdown_files):
    """Test that markdown content is correctly converted to HTML."""
    _convert_markdowns(setup_markdown_files["config"], setup_markdown_files["files"])
    index_html = (DST / "index.html").read_text()
    assert "<h1>Title</h1>" in index_html
    assert "<p>Some content." in index_html
    assert 'href="./index.html"' in index_html  # @root in root dir should be "./"

    page_html = (DST / "docs" / "page.html").read_text()
    assert "<h2>Subtitle</h2>" in page_html
    assert "<li>List item 1</li>" in page_html
    assert "List item 2" in page_html
    assert 'src="../images/logo.png"' in page_html  # @root in docs dir should be "../"


def test_convert_markdowns_creates_directories(fs, setup_markdown_files):
    """Test that directories are created as needed for markdown files."""
    fs.remove_object(str(DST))
    _convert_markdowns(setup_markdown_files["config"], setup_markdown_files["files"])
    assert DST.exists()
    assert (DST / "docs").exists()


def test_convert_markdowns_with_empty_list(setup_markdown_files):
    """Test that function works correctly with an empty file list."""
    _convert_markdowns(setup_markdown_files["config"], [])
    assert len(list(DST.iterdir())) == 0


def test_convert_markdowns_verbose_output(setup_markdown_files, capsys):
    """Test that verbose output is generated when verbose=True."""
    setup_markdown_files["config"]["verbose"] = True
    _convert_markdowns(setup_markdown_files["config"], setup_markdown_files["files"])
    captured = capsys.readouterr()
    assert "Converted index.md to HTML" in captured.out
    assert "Converted docs/page.md to HTML" in captured.out
    assert "Converted docs/subdir/deep.md to HTML" in captured.out


def test_root_replacement_at_different_depths(setup_markdown_files):
    """Test that @root is correctly replaced with the relative path to root based on file depth."""
    _convert_markdowns(setup_markdown_files["config"], setup_markdown_files["files"])

    # Root directory (depth 0) - @root should be "./"
    index_html = (DST / "index.html").read_text()
    assert 'href="./index.html"' in index_html

    # Depth 1 directory - @root should be "../"
    page_html = (DST / "docs" / "page.html").read_text()
    assert 'src="../images/logo.png"' in page_html

    # Depth 2 directory - @root should be "../../"
    deep_html = (DST / "docs" / "subdir" / "deep.html").read_text()
    assert 'href="../../index.html"' in deep_html
    assert 'href="../../docs/page.html"' in deep_html
