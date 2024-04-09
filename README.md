<picture>
   <source media="(prefers-color-scheme: dark)" srcset="./docs/files/gitspaces.dark.png">
   <img width="150" alt="Light and Dark logos" src="./docs/files/gitspaces.light.png">
</picture>

# gitspaces - A git development workspace manager

> Coming in Spring 2024

## What is GitSpaces

GitSpaces is a structured folder/directory system for working concurrently on independent parallel development tasks within and across multiple proects.

For those of you with experience using, ahem, the ClearCase vcs, you're familiar with the concept of ClearCase Views. GitSpaces is clearcase view for git projects.

A GitSpace is an isolated workspace that has all of your project code where you can work on ONE THING. A GitSpace project is a collection of spaces (think independent clones) for the project. If you are asked to fix a bug or something else in parallel, you just open a new space and work there.

## Installation

gitspaces is implemented in Go, so

1. [Install Go](https://go.dev/doc/install)
   
2. Install GitSpaces  
   [![Go Reference](https://pkg.go.dev/badge/github.com/davfive/gitspaces/v2.svg)](https://pkg.go.dev/github.com/davfive/gitspaces/v2)
   ```
   $ go install github.com/davfive/gitspaces/v2@latest
     -> installs to ~/go/bin/gitspaces

   $ gitspaces -v # to be change to gitspaces setup
     -> run once to install config and shell wrapper files to ~/.gitspaces/ (or C:/Users/<user>/.gitspaces/
   ```
4. Setup gitspaces command wrapper
   Some gitspaces commands change the current working directory of the user. To accomplish this, gitspaces is run through a shell (bash / powershell) wrapper.

   * MacOS
      * bash
        ```
        $ echo ". ~/.gitspaces/gitspaces.sh" >> ~/.bashrc   # main wrapper
        $ echo "alias gs=gitspaces" >> ~/.bashrc            # optional alias
        ```
      * PowerShell
        $ open 
   $ vim ~/.gitspaces/config.yaml
     -> update ProjectPaths list
   $ vim ~/.bashrc (or ~/.zshrc)
     -> add '. ~/.gitspaces/shellfunction.sh'
     -> add 'alias gs=gitspaces' (optional)
   $ . ~/.bashrc (or ~/.zshrc)
   ```

5. Create a GitSpace project
   ```
   $ cd /path/to/one/of/ProjectPaths
   $ gitspaces create REPO_URL
     -> creates project and cd's into space
   ```

6. Start using GitSpaces

## Commands

### The `gitspaces` command 
#### USAGE
`gitspaces COMMAND`Simplify your life with `alias gs=gitspaces`.

#### WHERE
COMMAND  | Description
---------|------------------------
`create` | Creates a new GitSpace project from a git repo url
`switch` | Switch spaces. Default, same as `gitspaces` w/o a command.
`rename` | Rename a current gitspace
`sleep`  | Archive a gitspace and wakes up another one
`code`   | Launches Visual Studio Code Workspace for the space


## GitSpace Project Structure

```
~/.../projects
 └── project-a
     ├── __GITSPACES_PROJECT__              
     ├── .code-workspace
     │   └── project-a~active-1.code-workspace
     ├── .zzz
     │   ├── zzz-0/
     │   │   └──  ... repo cloned here
     │   ├── zzz-1/
     │   │   └── ... zzz-0 copied here
     │   ├── zzz-...
     │   └── zzz-N/
     ├── active-1/
     │   └── ... active repo/space
     ├── active-...
     └── active-N/
```

### GitSpace User Config
```
# Created first time gitspaces is run
~/.gitspaces/
 ├── config.yaml (must be filled in before use)
 ├── gitspaces.sh
 ├── gitspaces.cygwin.sh
 ├── gitspaces.ps1
 └── gitspaces.scriptblock.ps1
```

#### config.yaml

```yaml
~/.gitspaces/config.yaml

ProjectPaths:
    - /path/to/a/projects/directory
    - /path/to/another/directory
    - ...
```
