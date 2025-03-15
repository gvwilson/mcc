"""Utility functions and constants for McCole."""

from pathlib import Path
import tomli
import click

# Default configuration file path
DEFAULT_CONFIG_PATH = Path("pyproject.toml")
# Default source directory path
DEFAULT_SRC_PATH = "src"
# Default destination directory path
DEFAULT_DST_PATH = "docs"


def read_config(config_file, verbose, src, dst):
    """Read configuration from TOML file."""
    if not config_file.exists():
        raise click.FileError(str(config_file), hint="File not found")
    
    with config_file.open("rb") as f:
        toml_dict = tomli.load(f)
    
    config = toml_dict.get("tool", {}).get("mccole", {})
    config["verbose"] = verbose
    _build_config(config, "src", src, DEFAULT_SRC_PATH)
    _build_config(config, "dst", dst, DEFAULT_DST_PATH)
    
    return config


def _build_config(config, key, cmdline, default):
    """Set a configuration value with priority: 
    command-line arg > config file > default."""
    if cmdline is not None:
        config[key] = cmdline
    elif key not in config:
        config[key] = default
    return config
