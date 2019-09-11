echo "Running gitspaces ..."

export GITSPACES_USERCFG=~/.gitspacesrc.sh
[ -f $GITSPACES_USERCFG ] && . $GITSPACES_USERCFG

export GITSPACES_NAME=$(basename "${BASH_SOURCE[0]}")
export GITSPACES_DIR=$(dirname "${BASH_SOURCE[0]}")
export GITSPACES_CONFIG="${GITSPACES_CONFIG:=gitspaces.ini}"
export GITSPACES_SPACESDIR="${GITSPACES_SPACESDIR:=_}"
export GITSPACES_PROJDIRS=${GITSPACES_PROJDIRS:=}

# Load GitSpace
. "$GITSPACES_DIR/gitspaces-helpers.sh"
. "$GITSPACES_DIR/gitspaces-config.sh"
. "$GITSPACES_DIR/gitspaces-spaces.sh"
. "$GITSPACES_DIR/gitspaces-repos.sh"

# Main GitSpaces commands
function gitspace() {
	if [ "x$GITSPACES_DIR" == "x$(pwd)" ]; then
		gs_echoc $GS_ECHO_RED "Error: Cannot run gitspace from the gitspaces repo"
		return 1
	fi
	local spacesdir=$(gs_getspacesdir)
	if [ ! -d "$(gs_checkspacesdir --silent "$spacesdir")" ]; then
		gs_switch "$@"
	fi

	local cmd=$1
	shift
	case "$cmd" in
		cd)          gs_cdspace "$@"    ;;
		checkout|co) gs_repos checkout  ;;
		code)        gs_codespace       ;;
		sw|switch)   gs_switch - "$@"   ;;
		list|ls)     gs_repos list      ;;
		mv|move)     gs_mvspace "$@"    ;;
		pull)        gs_repos pull      ;;
		sleep)       gs_sleep           ;;
		# Default, and most common action
		*)
			echo "usage: $0 <command> [<args>]"
			echo "where <command>"
			echo "  cd [space|-] [repos] [path|relpath] - cd around space or across spaces"
			echo "  co      - checkout BranchSet in all repos in space"
			echo "  code    - launch Visual Studio Code for this space"
			echo "  go      - change space"
			echo "  move/mv - rename space"
			echo "  pull    - fetch/pull all repos in space"
			echo "  list/ls - get repository info for all repos in space"
			echo "  sleep   - put current space to sleep."
			echo "  switch  - switch GitSpace projects (from GITSPACES_PROJDIRS list)"
			;;
	esac
}
