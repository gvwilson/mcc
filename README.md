# McCole: a simple static site generator

Re-writing the McCole SSG from scratch using [Claude Code][claude].

## Notes

1.  Using [uv][uv] for project management.
    -   Claude often fails to run commands inside the virtual environment.
1.  Claude creates the [click][click]-based CLI correctly.
    -   It adds too many comments to the code,
        and the comments it adds just repeat information that can be gleaned from variable and function names.
1.  Claude correctly added code to load configuration from a custom section of `pyproject.toml`.
    -   And did a good job refactoring that code to remove duplication when prompted.
1.  Struggled and eventually failed when asked to write tests using [pyfakefs][pyfakefs].
    -   Created good tests (e.g., included a test for "no files to copy" without extra prompting).
    -   But was unable to resolve type mis-match problems: pyfakefs needs strings, not `Path` objects.
    -   Repeatedly tried to convert usage of `Path` to low-level string manipulations.

[claude]: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview
[click]: https://click.palletsprojects.com/
[pyfakefs]: https://pytest-pyfakefs.readthedocs.io/
[uv]: https://docs.astral.sh/uv/
