# 
# Overridable Options
#

## GITSPACES_SPACESDIR
# Specify the name for the directory that contains all of the project spaces
#  <project-dir>/<spaces-dir>/<spaces>, default is _
#export GITSPACES_SPACESDIR="_"

## GITSPACES_PROJDIRS
# A space separated list of gitspace project dirs.
# This allows 'gs project' to know where all of your project dirs are
export GITSPACES_PROJDIRS="~/code/work/aurora ~/code/work/halo ~/code/work/lumen"

# 
# Recommended Aliases
#

alias gs=gitspace   # so you can just type gs cd, gs co, gs sleep, ...
alias cds='gs cd'   # way easier to type cds <dir> than gs cd <dir> all the time