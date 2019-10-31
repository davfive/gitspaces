echo "Running gitspaces.repos ..."

function gs_runRepoCommand() {
	# usage: $0 [<cmd-args...>] <cmd> / $0 [<repo> <cmd-args...>] <cmd> 
	if [ $# -eq 0 ]; then gs_echoc $GS_ECHO_RED "Internal Error: gs_runRepoCommand $@"; return 1; fi

	local repo args cmd
	gs_repoExists "$1"
	if [ $? -eq 0 ]; then repo=$1 ; shift ; fi
	[ $# -eq 1 ] && cmd=$1 || cmd=${@:(-1)}
	[ $# -eq 1 ] && args=() || args=( ${@:1:$#-1} )
	case "x$repo" in
		x) (set -x ; $cmd "${args[@]}") 2> /dev/null ;;
		*) (gs_cdspace $repo && set -x && $cmd "${args[@]}") 2> /dev/null ;;
	esac
}

# Must not use with gs_runRepoCommand to avoid endless recursion
function gs_repoExists() { test -d "$(git rev-parse --show-toplevel)/../$1"; }

# Call directly to do it on current repo or gs_repo* <space> <repo> to do it on different one
function gs_repoCheckout() { gs_runRepoCommand "$@" "git checkout"; }
function gs_repoGetName() { gs_runRepoCommand "$@" "git remote get-url origin" | xargs basename -s '.git'; }
function gs_repoGetBranch() { gs_runRepoCommand "$@" "git rev-parse --abbrev-ref HEAD"; }
function gs_repoGetRoot() { gs_runRepoCommand "$@" "git rev-parse --show-toplevel"; }
function gs_repoFetch() { gs_runRepoCommand "$@" "git fetch"; }
function gs_repoIsClean() { test $(gs_repoStatusUno "$@" | wc -l) -eq 0; } 
function gs_repoIsDirty() { test $(gs_repoStatusUno "$@" | wc -l) -gt 0; } 
function gs_repoPull() { gs_runRepoCommand "$@" "git pull"; }
function gs_repoStash() { gs_runRepoCommand "$@" "git stash"; }
function gs_repoStatus() { gs_runRepoCommand "$@" "git status --short"; }
function gs_repoStatusBranch() { gs_repoStatus "$@" --branch; }
function gs_repoStatusUno() { gs_repoStatus "$@" -uno; }

function gs_repoStashAsk() {
	gs_repoIsClean "$@" && return 0                  # Clean repo, no stash required
	echo "Modified files found:"; gs_repoStatus "$@" # Repo dirty, show modified files
  gs_askyesno "Stash before continuing?" || return 1   # Return 1 b/c chose not to stash, still dirty
	gs_repoStash "$@";                               # Return 0 == clean, 1 = failed, still dirty
}

# Same Space, Cross-Repository Actions
function gs_repos() {
	local spacesdir=$(gs_getspacesdir)
	local currepo=$(gs_repoGetName)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	case "$1" in
		checkout|co)
			local brset=$(gs_config_brset_select)
			local space=$(gs_getspace)
			local currrepo=$()
			for repo in $(gs_lsrepos); do
				local newbr=$(gs_config get "BranchSet:$brset" "$repo")
				local oldbr=$(gs_repoGetBranch $repo)

				gs_echoc $GS_ECHO_BLUE $(printf '=%.0s' {1..80})
				gs_echoc $GS_ECHO_BLUE "Checkout repo '$repo' to latest of branch '$newbr' "

				if [ "x$newbr" == "x" -o "x$newbr" == "x$oldbr" ]; then
					echo "Repo already on branch $oldbr"
				
				else
					local action="Change $repo from branch $oldbr to $newbr"
					gs_askyesno "Do you want to switch branches?"
					if [ $? -ne 0 ]; then
						gs_echoc $GS_ECHO_RED "Warning: Staying on existing branch '$oldbr' (and skipped 'git pull')"
						continue
					fi

					gs_repoStashAsk $repo
					if [ $? -ne 0 ]; then
						gs_echoc $GS_ECHO_RED "Warning: Chose to not change branch/pull for repo $repo"
						continue
					fi

					gs_repoCheckout $repo $newbr
					local currbr=$(gs_repoGetBranch $repo)
					if [ "x$currbr" != "x$newbr" ]; then
						gs_echoc $GS_ECHO_RED "Error: Failed to change to new branch '$newbr'"
						return 1
					fi
				fi

				# For all cases now that we are on the correct branch
				gs_repoStashAsk $repo
				if [ $? -ne 0 ]; then
					gs_echoc $GS_ECHO_RED "Warning: Skipping pull for repo $repo"
					continue
				fi

				# Pull Latest Changes
				echo "Pulling latest changes for branch $oldbr ..."
				gs_repoPull $repo
				if [ $? -ne 0 ]; then
					gs_echoc $GS_ECHO_RED "Error: Failed to pull latest changes"
					return 1
				fi
			done
			return 0
			;;
		list) # Current Working Branches
			echo "Repository Info for "$(gs_getspace)":"
			for repo in $(gs_lsrepos); do
				local br=$(gs_repoGetBranch $repo)
				printf "  %-15s %s\n" "$repo" "$br"
			done
			;;
		pull)
			local spaces
			case "$2" in
				-a|--all) spaces=( $(gs_lsspaces) ) ;;
				*)        spaces=( $(gs_getspace) ) ;;
			esac

			local space
			for space in "${spaces[@]}"; do
				local branch
				local spacedir="$spacesdir/$space"
				for repo in $(gs_lsrepos); do
					branch=$(gs_repoGetBranch $repo)
					gs_tsecho "Pulling $space::$repo [$branch]"

					# For all cases now that we are on the correct branch
					gs_repoIsDirty $repo && gs_askyesno "Stash required before pull. Stash then pull anyway?"
					if [ $? -eq 0 ]; then
						gs_repoStash $repo
					else
						gs_echoc $GS_ECHO_RED "Warning: Skipping pull for repo $repo"
						continue
					fi

					gs_repoPull $repo
					[ $? -ne 0 ] && return 1
				done
			done
			return 0
			;;
		*)
			return 1
			;;
	esac
}
