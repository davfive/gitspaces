# Repository-wide Copilot Instructions — davfive/gitspaces

You are GitHub Copilot (@copilot). Be concise and action-oriented. Prefer exact commands and copy/paste-ready file contents.

## Repository Overview
Python CLI tooling for managing “gitspaces”. Code lives under `src/gitspaces/` with pytest-based tests in `tests/`. CI runs via `.github/workflows/`.

- Entry points: `src/gitspaces/__main__.py` and `src/gitspaces/cli.py`
- Commands implemented under `src/gitspaces/modules/cmd_*.py` (e.g., `cmd_clone.py`, `cmd_setup.py`)
- Core helpers: `modules/config.py`, `path.py`, `project.py`, `space.py`, `console.py`, `errors.py`

## Developer Workflow
- Create venv: `python3 -m venv venv && . venv/bin/activate`
- Install deps: `pip install -r requirements-dev.txt`
- Run tests: `pytest -q`
- Lint/format: use tools declared in `pyproject.toml` if present; otherwise keep style consistent with existing files.
- Run CLI locally: `python -m gitspaces --help` (with `src/` on `PYTHONPATH`) or `python -m src.gitspaces` during development.

## Patterns & Conventions
- CLI pattern: subcommands map to `modules/cmd_<name>.py` with a function that wires into `cli.py`. Follow existing argument parsing style.
- Errors: use `modules/errors.py` types; raise specific exceptions and let CLI handle rendering via `console.py`.
- Paths: use `modules/path.py` helpers for filesystem operations; avoid manual `os.path` logic where helpers exist.
- Projects/Spaces: state and metadata are modeled in `project.py` and `space.py`; prefer these abstractions over ad-hoc dicts.
- Config: read/update via `modules/config.py`; keep configuration IO centralized.
- Tests: mirror command behavior under `tests/test_cmd_*.py`; for helpers, see `tests/test_*.py`. Prefer parametric tests and fixtures in `tests/conftest.py`.

## CI & Local Parity
- Workflows: see `.github/workflows/` (e.g., `test-all.yml`). Keep tests deterministic and fast; avoid network calls in unit tests.
- If adding new commands, include tests and ensure `pytest -q` passes locally before pushing.

## Integration Points
- External tools: the CLI shell integrations live in `modules/runshell.py`. Use it for spawning processes rather than `subprocess` directly.
- Editor/code invocation: `cmd_code.py` handles launching editors/VS Code; emulate its pattern for new editor interactions.

## File/Change Presentation
- Show complete file contents for new or changed files with headers: `name=<path> url=<permalink>`.
- For markdown proposals, wrap with four backticks to preserve internal code fences.
- For runnable scripts in chat, start with:
  ```bash
  set -euxo pipefail
  ```
  and include brief “Because:” / “Afterward:” comments for each command section.

## Example: Adding a New Subcommand
- Create `src/gitspaces/modules/cmd_example.py` implementing the action using `path.py`/`project.py` helpers.
- Wire into `src/gitspaces/cli.py` by registering the subcommand consistent with existing commands.
- Tests: add `tests/test_cmd_example_integration.py` covering typical and edge cases; use fixtures from `conftest.py`.

## PR Discipline
- One logical change per PR; update docs in `README.md` if user-facing behavior changes.
- Keep CI green; replicate CI steps locally (`pytest -q`).

Feedback: If any section is unclear or incomplete, tell me what you need expanded (e.g., exact CLI wiring points or test fixtures usage) and I’ll refine these instructions.
```
