# GitSpaces - A Git Development Workspace Manager

[![PyPI version](https://badge.fury.io/py/gitspaces.svg)](https://badge.fury.io/py/gitspaces)
[![Python Tests](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml/badge.svg)](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml)
[![Security Scan](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml/badge.svg)](https://github.com/davfive/gitspaces/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitspaces.svg)](https://pypi.org/project/gitspaces/)

> **Manage multiple independent clones of a git project seamlessly**

If you're familiar with ClearCase Views, think of GitSpaces as their counterpart for Git projects. If not, you're in for a treat!

GitSpaces manages multiple independent clones (called "spaces") of a project, allowing you to work on different features, bugs, or experiments simultaneously without the overhead of switching branches or stashing changes.

## ✨ Features

- 🚀 **Multiple Workspaces**: Create multiple independent clones of the same repository
- 🔄 **Easy Switching**: Quickly switch between different workspaces
- 💤 **Space Management**: Put workspaces to "sleep" when not in use, wake them up when needed
- 🎯 **Simple CLI**: Intuitive command-line interface with familiar git-like commands
- 🔧 **Extensible**: Add more clones to your project at any time
- 🎨 **Editor Integration**: Open workspaces directly in your favorite editor

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install gitspaces
```

### From Source

```bash
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
pip install -e .
```

## 🚀 Quick Start

### 1. Initial Setup

Run the setup command to configure GitSpaces:

```bash
gitspaces setup
```

This will:
- Configure where you keep your git projects
- Set your preferred editor (VS Code, vim, etc.)

### 2. Clone a Repository

Instead of `git clone`, use `gitspaces clone`:

```bash
gitspaces clone https://github.com/user/repo.git -n 3
```

This creates a project structure like:

```
~/.../projects/
 └── repo/
     ├── __GITSPACES_PROJECT__
     ├── main/              # Active workspace
     └── .zzz/              # Sleeping workspaces
         ├── zzz-0/
         ├── zzz-1/
         └── zzz-2/
```

### 3. Work with Spaces

```bash
# Switch to a different space
gitspaces switch

# Put a space to sleep and wake another
gitspaces sleep

# Rename a space
gitspaces rename old-name new-name

# Add more clones to your project
gitspaces extend -n 2

# Open a space in your editor
gitspaces code
```

## 📚 Commands

| Command | Description |
|---------|-------------|
| `setup` | Configure GitSpaces for first-time use |
| `clone` | Clone a git repository as a GitSpaces project |
| `switch` | Switch to a different workspace |
| `sleep` | Put a workspace to sleep and optionally wake another |
| `rename` | Rename a workspace |
| `extend` | Add more clone workspaces to the project |
| `code` | Open a workspace in your editor |
| `config` | View or edit configuration |

### Command Details

#### `gitspaces clone`

Clone a repository and create multiple workspaces:

```bash
gitspaces clone <url> [-n NUM_SPACES] [-d DIRECTORY]

# Examples:
gitspaces clone https://github.com/user/repo.git -n 3
gitspaces clone git@github.com:user/repo.git -n 5 -d ~/projects
```

#### `gitspaces switch`

Switch between workspaces interactively or directly:

```bash
gitspaces switch [SPACE_NAME]

# Interactive mode
gitspaces switch

# Direct switch
gitspaces switch feature-branch
```

#### `gitspaces sleep`

Put a workspace to sleep and optionally wake another:

```bash
gitspaces sleep [SPACE_NAME]
```

#### `gitspaces extend`

Add more clone workspaces to your project:

```bash
gitspaces extend -n NUM_SPACES [SOURCE_SPACE]

# Examples:
gitspaces extend -n 2           # Add 2 more clones from current space
gitspaces extend -n 3 main      # Add 3 clones from 'main' space
```

## 🏗️ Project Structure

When you clone a repository with GitSpaces, it creates:

```
project-name/
├── __GITSPACES_PROJECT__    # Marker file
├── space-1/                 # Active workspace 1
│   └── (full git clone)
├── space-2/                 # Active workspace 2
│   └── (full git clone)
└── .zzz/                    # Sleeping workspaces
    ├── zzz-0/
    ├── zzz-1/
    └── zzz-2/
```

## ⚙️ Configuration

GitSpaces stores its configuration in `~/.gitspaces/config.yaml`:

```yaml
project_paths:
  - /home/user/projects
  - /home/user/work
default_editor: code
```

### View Configuration

```bash
gitspaces config
```

### Set Configuration

```bash
gitspaces config default_editor vim
gitspaces config project_paths /path/to/projects
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📦 Deployment

For maintainers: See [README.DEPLOYMENT.md](README.DEPLOYMENT.md) for instructions on deploying to PyPI.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by ClearCase Views, reimagined for the Git era.

## 📞 Support

- 🐛 [Report bugs](https://github.com/davfive/gitspaces/issues)
- 💡 [Request features](https://github.com/davfive/gitspaces/issues)
- 📖 [Documentation](https://github.com/davfive/gitspaces#readme)

## 🗺️ Roadmap

- [ ] Workspace templates
- [ ] Branch synchronization helpers
- [ ] Workspace analytics
- [ ] Plugin system
- [ ] GUI interface

---

**Made with ❤️ by the GitSpaces team**
