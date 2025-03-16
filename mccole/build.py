"""Build functionality for McCole."""

import os
from pathlib import Path
import click
import shutil

from . import util


def do_build(config, verbose, src, dst):
    """Build the site."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config = util.read_config(config_file, verbose, src, dst)
    markdowns, others = util.find_files(config)
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
