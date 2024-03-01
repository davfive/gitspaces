<img src="gitspaces.png" width="100">

# gitspaces - A git development workspace manager

## Overview

GitSpaces creates multiple independent development environments (spaces) for a single repository.

A GitSpace projects are the containers to manage these spaces.

## Commands


Command     | Description
------------|------------------------
`gs switch` | Switch to a different top-level gitspace project. (default, runs with `gs` alone)
`gs switch` | Switch to a different top-level gitspace project.
`gs rename` | Rename a current gitspace
`gs sleep`  | Archive a gitspace (not using it currently - renames to _.zzz-# and hides from lists)
`gs cd`     | cd around a gitspaces project. Switch gitspace, repos, folder
`gs cd -`   | Switch to a different gitspace (allows you wake one up you put to sleep to use fresh)
`gs co`     | Choose from a list of 'BranchSet's (in gsconfig.ini) and will git pull each repos to it's specified branch
`gs code`   | Launches Visual Studio Code with .code-workspace file updated with proper paths for debugging
`gs init`   | _TODO_: Creates project gitspaces.ini, spaces-dir, and first gs space folder (firstspace)
`gs cp`     | _TODO_: Copies an existing gitspace folder to create another (and puts it to sleep)



## Project creation and layout
```
$ gitspaces create git@github.com:davfive/gitspaces.git -n NUM_SPACES 
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


## Background

The general idea is that for any given project you might be working on a feature here, a hotfix there, another feature there, 
and a bugfix somewhere else. You may handle all of these "concurrent" activities by forcing yourself to commit on your branch,
change branches, or stash stuff. I've found that to be a lot of overhead especially if you are coordinating this across multiple
repositories in a project.

For those of you with a, ahem, ClearCase background, you're familiar with the concept of ClearCase Views. Essentially it's an
isolated workspace that has all of your project code where you can work on ONE THING. If you are asked to fix a bug or
something else concurrently, you just create a new view (they're cheap) and work there. Unfortunately, git has no concept
like this. Clones are expensive, committing just to context switch is a pain and messes up your commit history to boot.

Gitspaces are essentially a lightweight implementation of ClearCase Views for git projects.

## Command overview

Once gitspaces scripts are available in your environment, all gitspaces commands are prefixed with `gs`. e.g.

Command     | Description
------------|------------------------
`gs switch` | Switch to a different top-level gitspace project.
`gs ls`     | List repository information (e.g., what branch they are on)
`gs mv`     | Rename a current gitspace
`gs sleep`  | Archive a gitspace (not using it currently - renames to _.zzz-# and hides from lists)
`gs cd`     | cd around a gitspaces project. Switch gitspace, repos, folder
`gs cd -`   | Switch to a different gitspace (allows you wake one up you put to sleep to use fresh)
`gs co`     | Choose from a list of 'BranchSet's (in gsconfig.ini) and will git pull each repos to it's specified branch
`gs code`   | Launches Visual Studio Code with .code-workspace file updated with proper paths for debugging
`gs init`   | _TODO_: Creates project gitspaces.ini, spaces-dir, and first gs space folder (firstspace)
`gs cp`     | _TODO_: Copies an existing gitspace folder to create another (and puts it to sleep)


## Quick Setup

1. Download/Clone gitspaces repo and add it to your .bashrc file

   ```
   cd ~
   git clone <repo-path> .gitspaces
   echo ". ~/.gitspaces/gitspaces.sh" >> ~/.bashrc
   cp ~/.gitspaces/userfiles/.gitspacesrc.sh  ~/
   perl -pi -e "s/^#alias/alias/ ~/.gitspacesrc.sh  # aliases gs=gitspaces, cds='gs cd'
   . ~/.bashrc
   ```
   
2. Create a code project folder (will house projectA's gitspaces)

   ```
   mkdir -p ~/code/projectA
   ```

3. Setup a GitSpaces project folder
   > Future: this is what 'gs init' will do
   ```
   cd ~/code/projectA
   cp ~/.gitspaces/userfiles/gitspaces.ini .        # See file comments for details
   mkdir $GITSPACES_SPACESDIR  # defaults to '_'    # Where all of your project spaces will live
   mkdir -p $GITSPACES_SPACESDIR/firstspace         # First project space, you can rename it later
   cd $GITSPACES_SPACESDIR/firstspace

   # A GitSpaces project folder has the following structure:
   ~/code/projectA/
    |- gitspaces.ini
    |- _/
       +- space-1/
          +- projectA-repo-1
          ...
          +- projectA-repo-N
       ...
       +- space-N/
          +- projectA-repo-1
          ...
          +- projectA-repo-N
   ```

4. Clone all of your repositories into the \_.first gitspace folder

   ```
   cd ~/code/projectA/_/firstspace
   git clone <projectA-repo1>
   ...
   git clone <projectA-repoN>
   ```
   
5. Create additional GitSpaces for projectA
   > Simply 'cp -R firstspace secondspace' (way faster usually than re-cloning)  
   > Note the copy operation is way quicker if you clean your firstspace repos' (git clean -dx -f)  
   ```
   cd ~/code/projectA
   cp -R firstspace secondspace
   ...
   cp -R firstspace nthspace
   ```
  
   You can add a new gitspace folder anytime you want when you need more. I've generally found that 5 are sufficient.

6. Add your new GitSpaces project to GITSPACES_PROJDIRS in ~/.gitspacesrc.sh and resource

7. Start using GitSpaces

8. Optional: Include ~/.gitspaces/userfiles/gitconfig

   My common git aliases are in the userfiles folder. Just add the following to your ~/.gitconfig
   
   ```
   [include]
   path = ~/.gitspaces/userfiles/gitconfig
   ```
