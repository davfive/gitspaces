<img src="gitspaces.png" width="100">

# gitspaces - A git development workspace manager

## Background

The general idea is that for any given project you might be working on a feature here, a hotfix there, another feature there, and a bugfix somewhere else. You may handle all of these "concurrent" activities by forcing yourself to commit on your branch, change branches, or stash stuff. I've found that to be a lot of overhead especially if you are coordinating this across multiple repositories in a project.

For those of you with a, ahem, ClearCase background, you're familiar with the concept of ClearCase Views. Essentially it's an isolated workspace that has all of your project code where you can work on ONE THING. If you are asked to fix a bug or something else concurrently, you just create a new view (they're cheap) and work there. Unfortunately, git has no concept
like this. Clones are expensive, committing just to context switch is a pain and messes up your commit history to boot.

GitSpaces are essentially a lightweight implementation of ClearCase Views for git projects.

GitSpace projects (made with `gitspaces create ...` ) are the containers to manage these spaces.

## Commands
`gitspaces COMMAND`. Simplify your life with `alias gs=gitspaces`.

COMMAND  | Description
---------|------------------------
`create` | Creates a new GitSpace project from a git repo url
`switch` | Switch to a different space (in the same or different project)
`rename` | Rename a current gitspace
`sleep`  | Archive a gitspace and wakes up another one
`code`   | Launches Visual Studio Code with .code-workspace

> [!NOTE]
> 1. Try `gitspaces -h` or `gitspaces COMMAND -h`
> 
> 2. `gitspaces code` opens a workspace not the folder, with the title `PROJECTNAME~SPACENAME` so you can differentiate windows.
> 
> 3. Running `gitspaces` by itself does a `gitspaces switch`

## Project creation and layout
`$ gitspaces create git@github.com:davfive/gitspaces.git -n NUM_SPACES 
`

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

## User options and dotfiles
```
# Created first time gitspaces is run
~/.gitspaces/
 ├── config.yaml (must be filled in before use)
 └── shells
     ├──  bashrc (bash wrapper function)
     └──  zshrc  (zsh wra...)
```

## User configuration file
`~/.gitspaces/config.yaml`
```yaml
ProjectPaths:
    - /path/to/a/projects/directory
    - /path/to/another/directory
    - ...
```

## Installation, setup, and first use

gitspaces is implemented in Go, so

1. [Install Go](https://go.dev/doc/install)  
   > then check that your GOPATH is set with `go env GOPATH`
   
2. run `go install github.com/davfive/gitspaces/v2@latest`  
   > It will be installed to $GOPATH/bin/gitspaces

3. TODO: put setup steps here

4. Run `gitspaces create REPO_URL` from your projects directory

5. Start using GitSpaces

## Still to do

1. Add support for multiple repositories in a space  
   > It can be easily done manually right now if you know how