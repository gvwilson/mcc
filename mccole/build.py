"""Build functionality for McCole."""

from bs4 import BeautifulSoup
import click
import markdown
from pathlib import Path
import shutil

from . import util

# Markdown extensions to enable
MARKDOWN_EXTENSIONS = [
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.fenced_code",
    "markdown.extensions.md_in_html",
    "markdown.extensions.tables",
]


def do_build(config, verbose, src, dst):
    """Build the site."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config = util.read_config(config_file, verbose, src, dst)
    markdowns, others = util.find_files(config)
    _convert_markdowns(config, markdowns)
    _copy_others(config, others)


def _copy_others(config, files):
    """Copy non-Markdown files from source to destination."""
    src_path = Path(config["src"])
    dst_path = Path(config["dst"])
    for file_path in files:
        file_path = Path(file_path)
        rel_path = file_path.relative_to(src_path)
        dest_file = dst_path / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest_file)
        if config["verbose"]:
            click.echo(f"Copied {rel_path}")


def _convert_markdowns(config, files):
    """Convert Markdown files to HTML."""
    src_path = Path(config["src"])
    dst_path = Path(config["dst"])
    for file_path in files:
        file_path = Path(file_path)
        rel_path = file_path.relative_to(src_path)
        dest_file = dst_path / rel_path.with_suffix(".html")
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "r") as md_file:
            md_content = md_file.read()

        html_content = markdown.markdown(md_content, extensions=MARKDOWN_EXTENSIONS)
        html_content = _do_root_path_replacement(html_content, rel_path)

        with open(dest_file, "w") as html_file:
            html_file.write(html_content)

        if config["verbose"]:
            click.echo(f"Converted {rel_path} to HTML")


def _do_root_path_replacement(html_content, rel_path):
    """Replace @root/ with the relative path to the root directory in HTML content."""
    # Calculate relative path to root
    depth = len(rel_path.parts) - 1
    root_path = "../" * depth if depth > 0 else "./"

    # Parse HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Attributes that might need @root/ replacement
    attributes = ["href", "src"]

    # Loop through each attribute type
    for attr in attributes:
        # Find all elements with this attribute
        for tag in soup.find_all(attrs={attr: True}):
            if tag[attr].startswith("@root/"):
                tag[attr] = tag[attr].replace("@root/", root_path)

    # Convert back to HTML string
    return str(soup)
