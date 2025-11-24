# GitSpaces

[![PyPI version](https://badge.fury.io/py/gitspaces.svg)](https://badge.fury.io/py/gitspaces)
[![Tests](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml/badge.svg)](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/pypi/pyversions/gitspaces.svg)](https://pypi.org/project/gitspaces/)

Manage multiple independent clones of a git repository. Similar to ClearCase Views but for Git.

Work on multiple features, branches, or experiments simultaneously without branch switching overhead. Each "space" is an independent clone of your repository.

> *Note: This project is currently at v3. It has evolved through several major iterations over the past 7 years — originally implemented as a collection of Bash scripts (v1), then rewritten in Go (v2), and now implemented in Python (v3). The prior v1/v2 repositories are archived and available at https://github.com/davfive/gitspaces.golang.*

## Features

- Multiple independent clones per repository
- Fast switching between workspaces
- Inactive spaces can be put to "sleep"
- Add more clones on demand
- Direct editor integration

## Installation

```bash
pip install gitspaces
```

Or from source:
```bash
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
pip install -e .
```

## Quick Start

Configure project paths and editor:
```bash
gitspaces setup
```

Clone a repository with multiple workspaces:
```bash
gitspaces clone https://github.com/user/repo.git -n 3
```

Creates:
```
projects/repo/
├── __GITSPACES_PROJECT__
├── main/          # active workspace
└── .zzz/          # sleeping workspaces
    ├── zzz-0/
    ├── zzz-1/
    └── zzz-2/
```

Basic operations:
```bash
gitspaces switch              # switch workspace
gitspaces sleep               # sleep active, wake another
gitspaces rename old new      # rename workspace
gitspaces extend -n 2         # add 2 more clones
gitspaces code                # open in editor
```

## Commands

```bash
gitspaces setup                           # configure project paths, editor
gitspaces clone <url> [-n N] [-d DIR]     # clone repo with N workspaces
gitspaces switch [SPACE]                  # switch workspace (interactive if no arg)
gitspaces sleep [SPACE]                   # sleep workspace, optionally wake another
gitspaces rename OLD NEW                  # rename workspace
gitspaces extend -n N [SOURCE]            # add N more clones
gitspaces code [SPACE]                    # open workspace in editor
gitspaces config [KEY] [VALUE]            # view/set configuration
```

## Configuration

Default location: `~/.gitspaces/config.yaml`

```yaml
project_paths:
  - /home/user/projects
default_editor: code
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Deployment

Maintainers: see [README.DEPLOYMENT.md](README.DEPLOYMENT.md) for PyPI deployment.

## License

MIT - see [LICENSE](LICENSE).
