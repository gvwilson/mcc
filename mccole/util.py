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


def find_files(config):
    """Find files in the source directory, returning (markdown, others)."""
    src_path = Path(config["src"])
    markdown_files = []
    other_files = []
    skips = config["skips"]

    for path in src_path.rglob("*"):
        if not path.is_file():
            pass
        elif any(path.match(pat) for pat in skips):
            pass
        elif path.suffix.lower() == ".md":
            markdown_files.append(path)
        else:
            other_files.append(path)

    return markdown_files, other_files


def read_config(config_file, verbose, src, dst):
    """Read configuration from TOML file."""
    if not config_file.exists():
        raise click.FileError(str(config_file), hint="File not found")

    with config_file.open("rb") as reader:
        toml_dict = tomli.load(reader)

    config = toml_dict.get("tool", {}).get("mccole", {})

    _check_config(
        config_file,
        config,
        "skips",
        lambda cfg, key: key not in cfg or isinstance(cfg[key], list),
        "'skips' in configuration must be a list of glob patterns"
    )

    config["verbose"] = verbose
    _build_config(config, "src", src, DEFAULT_SRC_PATH)
    _build_config(config, "dst", dst, DEFAULT_DST_PATH)
    _build_config(config, "skips", None, [])

    return config


def _build_config(config, key, cmdline, default):
    """Set a configuration value with priority:
    command-line arg > config file > default."""
    if cmdline is not None:
        config[key] = cmdline
    elif key not in config:
        config[key] = default
    return config


def _check_config(filename, config, key, check_func, error_msg):
    """Check that a configuration value satisfies a condition."""
    if not check_func(config, key):
        raise ValueError(f"{error_msg} in {filename}")
