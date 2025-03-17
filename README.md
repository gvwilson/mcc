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
1.  Claude added Markdown extensions correctly on the first try.
1.  Claude was able to write and refactor code to translate `@root` references in URLs.
    -   Wrote tests without being prompted explicitly (possibly because it noticed the `tests` directory?).
    -   Keeps wanting to add lines of whitespace and/or trailing whitespace in Python files.
1.  Claude added functions to handle bibliography and glossary references correctly on the first try.
    -   Also added tests and refactored when prompted to remove duplication.
    -   Though I was very specific about the refactoring I wanted.
    -   And refactored to loop over transformation functions correctly on the first try given a very specific prompt.

[claude]: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview
[click]: https://click.palletsprojects.com/
[pyfakefs]: https://pytest-pyfakefs.readthedocs.io/
[uv]: https://docs.astral.sh/uv/
