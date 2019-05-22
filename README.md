# gitspaces - A git development workspace manager

> NOTE: I am calling all things "scripts". They are actually no scripts at all that are called from the cmdline. They are all bash aliases and functions, but to have one word, I call everything scripts.

## Overview

GitSpaces is a set of bash scripts for managing git-based development workspaces. The main features are

1. Space management
   * Multiple spaces
   * Multiple repositories per space
   * Space hibernation
   * Space renaming
   * Per user, space configuration overrides
2. Cross-repository branch management
   * Common Development aids
   * Visual Studio Code configuration per workspace
   * Common (and uncommon) git alias
   * Directory change aliases (to each repository)

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

## Quick Setup

1. Create a code project folder

   `~/code/projectA`

2. Copy the gsconfig.ini file there.
   
   `~/code/projectA/gsconfig.ini`

3. Create 1 gitspace in the project folder (prefix it with _.

   `~/code/projectA/_.first`
   
4. Clone all of your repositories into the _.first folder

   ```
   ~/code/projectA/
   |- gsconfig.ini
   |- _.first/
      +- projectA-repo-1
      ...
      +- projectA-repo-N
   ```
