"""Build functionality for McCole."""

from bs4 import BeautifulSoup
import click
import jinja2
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
    jinja_env = _set_up_jinja(config)
    _convert_markdowns(config, jinja_env, markdowns)
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


def _convert_markdowns(config, jinja_env, files):
    """Convert Markdown files to HTML."""
    transformations = [
        _do_root_path_replacement,
        _do_bibliography_refs,
        _do_glossary_refs,
        _do_markdown_to_html_links
    ]
    src_path = Path(config["src"])
    dst_path = Path(config["dst"])
    template = jinja_env.get_template(util.DEFAULT_TEMPLATE_PAGE)

    for file_path in files:
        file_path = Path(file_path)
        rel_path = file_path.relative_to(src_path)
        dest_file = dst_path / rel_path.with_suffix(".html")
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "r") as md_file:
            md_content = md_file.read()

        html_content = markdown.markdown(md_content, extensions=MARKDOWN_EXTENSIONS)
        soup = BeautifulSoup(html_content, "html.parser")
        for transform in transformations:
            soup = transform(soup, rel_path)

        content = str(soup)
        final_html = template.render(content=content, page_path=rel_path)

        with open(dest_file, "w") as html_file:
            html_file.write(final_html)

        if config["verbose"]:
            click.echo(f"Converted {rel_path} to HTML")


def _create_root_path(rel_path):
    """Calculate the relative path to the root directory."""
    depth = len(rel_path.parts) - 1
    return "../" * depth if depth > 0 else "./"


def _do_bibliography_refs(soup, rel_path):
    """Replace b:something links with relative references to bibliography.html#something."""
    root_path = _create_root_path(rel_path)

    for tag in soup.find_all("a", href=True):
        if tag["href"].startswith("b:"):
            ref_id = tag["href"][2:]
            tag["href"] = f"{root_path}bibliography.html#{ref_id}"

    return soup


def _do_glossary_refs(soup, rel_path):
    """Replace g:something links with relative references to glossary.html#something."""
    root_path = _create_root_path(rel_path)

    for tag in soup.find_all("a", href=True):
        if tag["href"].startswith("g:"):
            ref_id = tag["href"][2:]
            tag["href"] = f"{root_path}glossary.html#{ref_id}"

    return soup


def _do_markdown_to_html_links(soup, rel_path):
    """Replace .md links with .html links."""
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if ".md" in href:
            # Handle both simple .md and .md#anchor cases
            if href.endswith(".md"):
                tag["href"] = href[:-3] + ".html"
            elif ".md#" in href:
                # Replace .md with .html but preserve the anchor
                tag["href"] = href.replace(".md#", ".html#")

    return soup


def _do_root_path_replacement(soup, rel_path):
    """Replace @root/ with the relative path to the root directory in HTML content."""
    root_path = _create_root_path(rel_path)

    # Attributes that might need @root/ replacement
    attributes = ["href", "src"]

    # Loop through each attribute type
    for attr in attributes:
        # Find all elements with this attribute
        for tag in soup.find_all(attrs={attr: True}):
            if tag[attr].startswith("@root/"):
                tag[attr] = tag[attr].replace("@root/", root_path)

    return soup


def _set_up_jinja(config):
    """Set up Jinja2 environment."""
    templates_path = Path(config["templates"])
    if not templates_path.exists():
        raise click.ClickException(f"Templates directory '{templates_path}' does not exist")

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path),
        autoescape=jinja2.select_autoescape(["html", "xml"])
    )
