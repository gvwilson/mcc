"""Tests for build functionality."""

from bs4 import BeautifulSoup
from pathlib import Path
import pytest

from mccole.build import (
    _copy_others,
    _convert_markdowns,
    _do_markdown_to_html_links,
    _set_up_jinja,
)

# Directories (using non-defaults to improve testing).
SRC = Path("/source")
DST = Path("/dest")
TEMPLATES = Path("/templates")


@pytest.fixture
def setup_files(fs):
    """Set up test files and directories in the fake filesystem."""
    fs.create_dir(str(SRC))
    fs.create_dir(str(DST))
    fs.create_dir(str(TEMPLATES))
    fs.create_file(str(TEMPLATES / "page.html"), contents="<!DOCTYPE html>\n<html>\n<body>\n{{ content|safe }}\n</body>\n</html>")

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
    config = {"src": SRC, "dst": DST, "verbose": False, "templates": TEMPLATES}

    return {"files": files, "config": config}


@pytest.fixture
def setup_markdown_files(fs):
    """Set up test Markdown files and directories in the fake filesystem."""
    fs.create_dir(str(SRC))
    fs.create_dir(str(DST))
    fs.create_dir(str(TEMPLATES))
    fs.create_file(str(TEMPLATES / "page.html"), contents="<!DOCTYPE html>\n<html>\n<body>\n{{ content|safe }}\n</body>\n</html>")

    files = []
    files.append(
        fs.create_file(
            str(SRC / "index.md"),
            contents="# Title\n\nSome content.\n[Link to root](@root/index.html)\n[Citation 1](b:citation1)\n[Glossary term](g:term1)",
        )
    )
    fs.create_dir(str(SRC / "docs"))
    files.append(
        fs.create_file(
            str(SRC / "docs" / "page.md"),
            contents="## Subtitle\n\n- List item 1\n- List item 2\n<img src='@root/images/logo.png'>\n[Another citation](b:citation2)\n[Another term](g:term2)",
        )
    )
    fs.create_dir(str(SRC / "docs" / "subdir"))
    files.append(
        fs.create_file(
            str(SRC / "docs" / "subdir" / "deep.md"),
            contents="### Deep page\n\n[Back to home](@root/index.html)\n[To page](@root/docs/page.html)\n[Deep citation](b:citation3)\n[Deep term](g:term3)",
        )
    )
    files = [f.path for f in files]

    # Config uses strings for compatibility
    config = {"src": SRC, "dst": DST, "verbose": False, "templates": TEMPLATES}

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
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])
    assert (DST / "index.html").exists()
    assert (DST / "docs" / "page.html").exists()


def test_convert_markdowns_converts_content(setup_markdown_files):
    """Test that markdown content is correctly converted to HTML."""
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])
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
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])
    assert DST.exists()
    assert (DST / "docs").exists()


def test_convert_markdowns_with_empty_list(setup_markdown_files):
    """Test that function works correctly with an empty file list."""
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, [])
    assert len(list(DST.iterdir())) == 0


def test_convert_markdowns_verbose_output(setup_markdown_files, capsys):
    """Test that verbose output is generated when verbose=True."""
    setup_markdown_files["config"]["verbose"] = True
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])
    captured = capsys.readouterr()
    assert "Converted index.md to HTML" in captured.out
    assert "Converted docs/page.md to HTML" in captured.out
    assert "Converted docs/subdir/deep.md to HTML" in captured.out


def test_root_replacement_at_different_depths(setup_markdown_files):
    """Test that @root is correctly replaced with the relative path to root based on file depth."""
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

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


def test_bibliography_refs_at_different_depths(setup_markdown_files):
    """Test that b:id links are correctly replaced with bibliography.html#id based on file depth."""
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    # Root directory (depth 0) - should link to ./bibliography.html
    index_html = (DST / "index.html").read_text()
    assert 'href="./bibliography.html#citation1"' in index_html

    # Depth 1 directory - should link to ../bibliography.html
    page_html = (DST / "docs" / "page.html").read_text()
    assert 'href="../bibliography.html#citation2"' in page_html

    # Depth 2 directory - should link to ../../bibliography.html
    deep_html = (DST / "docs" / "subdir" / "deep.html").read_text()
    assert 'href="../../bibliography.html#citation3"' in deep_html


def test_glossary_refs_at_different_depths(setup_markdown_files):
    """Test that g:id links are correctly replaced with glossary.html#id based on file depth."""
    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    # Root directory (depth 0) - should link to ./glossary.html
    index_html = (DST / "index.html").read_text()
    assert 'href="./glossary.html#term1"' in index_html

    # Depth 1 directory - should link to ../glossary.html
    page_html = (DST / "docs" / "page.html").read_text()
    assert 'href="../glossary.html#term2"' in page_html

    # Depth 2 directory - should link to ../../glossary.html
    deep_html = (DST / "docs" / "subdir" / "deep.html").read_text()
    assert 'href="../../glossary.html#term3"' in deep_html


def test_bibliography_refs_only_transforms_b_links(setup_markdown_files, fs):
    """Test that only b:id links are transformed and other links are left unchanged."""
    # Add a file with both bibliography and normal links
    mixed_file = SRC / "mixed_links.md"
    fs.create_file(
        str(mixed_file),
        contents=(
            "# Page with mixed links\n\n"
            "[Bibliography link](b:citation4)\n"
            "[Normal link](https://example.org)\n"
            "[Relative link](./local.html)\n"
            "[Root link](@root/index.html)"
        ),
    )
    setup_markdown_files["files"].append(str(mixed_file))

    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    mixed_html = (DST / "mixed_links.html").read_text()

    # Bibliography link should be transformed
    assert 'href="./bibliography.html#citation4"' in mixed_html

    # Other links should be unchanged (except @root which is handled separately)
    assert 'href="https://example.org"' in mixed_html
    assert 'href="./local.html"' in mixed_html
    assert 'href="./index.html"' in mixed_html  # @root transformation


def test_glossary_refs_only_transforms_g_links(setup_markdown_files, fs):
    """Test that only g:id links are transformed and other links are left unchanged."""
    # Add a file with glossary and other link types
    mixed_file = SRC / "mixed_glossary_links.md"
    fs.create_file(
        str(mixed_file),
        contents=(
            "# Page with mixed links\n\n"
            "[Glossary term](g:term4)\n"
            "[Bibliography link](b:citation4)\n"
            "[Normal link](https://example.org)\n"
            "[Relative link](./local.html)\n"
            "[Root link](@root/index.html)"
        ),
    )
    setup_markdown_files["files"].append(str(mixed_file))

    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    mixed_html = (DST / "mixed_glossary_links.html").read_text()

    # Glossary link should be transformed
    assert 'href="./glossary.html#term4"' in mixed_html

    # Bibliography link should also be transformed (by the bibliography handler)
    assert 'href="./bibliography.html#citation4"' in mixed_html

    # Other links should be unchanged (except @root which is handled separately)
    assert 'href="https://example.org"' in mixed_html
    assert 'href="./local.html"' in mixed_html
    assert 'href="./index.html"' in mixed_html  # @root transformation


def test_markdown_to_html_links_conversion(setup_markdown_files, fs):
    """Test that .md links are converted to .html links."""
    # Add a file with markdown links
    md_links_file = SRC / "markdown_links.md"
    fs.create_file(
        str(md_links_file),
        contents=(
            "# Page with Markdown links\n\n"
            "[Link to another page](another-page.md)\n"
            "[Link to nested page](docs/nested.md)\n"
            "[Link with anchor](page.md#section)\n"
            "[External link](https://example.org/file.md)\n"
        ),
    )
    setup_markdown_files["files"].append(str(md_links_file))

    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    html_content = (DST / "markdown_links.html").read_text()

    # Markdown links should be transformed to HTML links
    assert 'href="another-page.html"' in html_content
    assert 'href="docs/nested.html"' in html_content
    assert 'href="page.html#section"' in html_content

    # External links with .md should still be transformed
    # (This is expected behavior, as the function only checks for .md at the end)
    assert 'href="https://example.org/file.html"' in html_content


def test_markdown_links_with_mixed_content(setup_markdown_files, fs):
    """Test that markdown link conversion works alongside other transformations."""
    # Add a file with mixed types of links including markdown links
    mixed_file = SRC / "mixed_md_links.md"
    fs.create_file(
        str(mixed_file),
        contents=(
            "# Page with mixed link types\n\n"
            "[Markdown link](page.md)\n"
            "[Bibliography link](b:citation5)\n"
            "[Glossary term](g:term5)\n"
            "[Root link](@root/docs/page.md)\n"
            "[External markdown](https://example.org/file.md)\n"
        ),
    )
    setup_markdown_files["files"].append(str(mixed_file))

    jinja_env = _set_up_jinja(setup_markdown_files["config"])
    _convert_markdowns(setup_markdown_files["config"], jinja_env, setup_markdown_files["files"])

    html_content = (DST / "mixed_md_links.html").read_text()

    # Check that all transformations are applied correctly
    assert 'href="page.html"' in html_content  # Markdown to HTML
    assert 'href="./bibliography.html#citation5"' in html_content  # Bibliography
    assert 'href="./glossary.html#term5"' in html_content  # Glossary
    assert 'href="./docs/page.html"' in html_content  # @root + .md to .html
    assert 'href="https://example.org/file.html"' in html_content  # External .md to .html


def test_do_markdown_to_html_links_function(setup_markdown_files):
    """Test the _do_markdown_to_html_links function directly."""
    # Create a test HTML string with various types of links
    html = """
    <html>
    <body>
        <a href="page.md">Regular Markdown link</a>
        <a href="folder/page.md">Nested Markdown link</a>
        <a href="page.md#section">Markdown link with anchor</a>
        <a href="https://example.org/file.md">External Markdown link</a>
        <a href="page.html">Already HTML link</a>
        <a href="https://example.org">Regular link</a>
        <a href="b:citation">Bibliography link</a>
        <a href="g:term">Glossary link</a>
    </body>
    </html>
    """
    
    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")
    
    # Apply the transformation
    result = _do_markdown_to_html_links(soup, Path("index.md"))
    
    # Convert back to string for checking
    result_html = str(result)
    
    # Check that all .md links were converted to .html
    assert 'href="page.html"' in result_html
    assert 'href="folder/page.html"' in result_html
    assert 'href="page.html#section"' in result_html
    assert 'href="https://example.org/file.html"' in result_html
    
    # Check that other links were not modified
    assert 'href="https://example.org"' in result_html
    assert 'href="b:citation"' in result_html
    assert 'href="g:term"' in result_html
