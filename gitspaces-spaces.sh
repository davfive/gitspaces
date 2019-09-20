echo "Running gitspaces.spaces ..."
# WARNING - Because you can have multiple sets of spaces on your system, the GitSpaces
#           scripts will exit out if you are not in either the top-level GitSpaces dir
#           or down inside one of it's spaces
#
# GitSpace infrastructure to manage multiple git repository instances
# If another one is needed, don't re-clone everything, just cp -R an existing one to a new folder.
#
# Available Commands:
#   cd*     - cd based on repos alias cc=ccapp, th=thunderhead, ... (see bottom of file for all)
#   codev   - Open code workspace for dev
#   lsdev   - list all development environments
#   lsdevbr - list branches for each repos in space
#   mvdev   - rename the current dev environment
#   zdev    - Puts dev to sleep (unuzed).

# Encapsulate error message and checking. Call like:
#  [ ! -d "$(gs_checkspacesdir $spacesdir)" ] && return 1
function gs_checkspacesdir() {
	local silent=false
	if [ "$1" == "--silent" ]; then
		shift
		silent=true
	fi 

	if [[ ! -d "$1" || "$1" == "$GITSPACES_DIR" ]]; then
    # gitspaces libdir can be confused as a space
		if [ "silent" = false ]; then
			>&2 echo "Not in a GitSpace. cd into a GitSpace to run commands."
		fi
		return 1
	fi
	echo $1
	return 0
}

function gs_getspacesdir() {
	local dir=$(pwd)
	while [ "$dir" != '/' ]; do
		if [ -f "$dir/$GITSPACES_CONFIG" ]; then
			echo $dir/$GITSPACES_SPACESDIR
			return 0
		fi
		dir=$(dirname "$dir")
	done
	return 1
}

# Switch to another gitspace
function gs_switch() {
	if [ "x$GITSPACES_PROJDIRS" == "x" ]; then
		echo "Error: GITSPACES_PROJDIRS array empty. Set 'export GITSPACES=(gitspace1_dir gitspace2_dir ...)' in your .bashrc file"
		return 1
	fi

	# Still don't have it? Look it up
	local gsproject
	while [ "x$gsproject" == "x" ]; do
		PS3="Select GitSpaces Project: "
		select gsproject in ${GITSPACES_PROJDIRS}; do
			break
		done
	done
	cd $(eval echo $gsproject) # force ~ expansion from GITSPACES space separated
	
	gs_cdspace "$@"
}

# Open Visual Studio Code for this dev environment
function gs_codespace() {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	space=$(gs_getspace)
	(cd $spacesdir/$space; code .)
}

function gs_getspace() {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	# Exit code indicates whether I used $1 for space (0=yes, 1=no)
	local space=
	local ret=0

	# If I've passed one in that exists, use it	
	if [ $# -eq 1 ]; then
		space=$(gs_isspace $1)
		if [[ $? == 0 || "x$1" == "x-" ]]; then
			ret=1 # Cheated and used $1
		fi
	fi

	# If not passed, try to sniff it from the current path ('-' overrides to lookup)
	if [[ "x$space" == "x" && "x$1" != "x-" ]]; then
		space=$(echo $(pwd) | awk -F$spacesdir/ '{ print $2 }' | awk -F/ '{ print $1 }' )
		space=$(gs_isspace $space) # double check
	fi

	# Still don't have it? Look it up
	while [ "x$space" == "x" ]; do
		PS3="Select GitSpace: "
		local spaces=$(gs_lsspaces | grep -v '.zzz-')

		local numzzzs=$(gs_sleep -c)
		local choosez
		if [ $numzzzs -gt 0 ]; then
			choosez="zzz($numzzzs)"
		fi
		select space in $spaces $choosez; do
			break
		done
		if [[ "$space" = zzz* ]]; then
			space=$(gs_sleep -n)
		fi
	done
	basename $space
	return $ret # 0 if used $1, 1 if I didn't
}

function gs_isspace()  {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	if [ -d $spacesdir/$1 ]; then echo $1; return 0;
	else return 1;
	fi
}

function gs_lsspaces() {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	(cd $spacesdir; find .  -maxdepth 1 -type d | grep -v -x '.' | sort | xargs basename -a)
}

function gs_lsrepos() {
	local spacesdir=${spacesdir:=$(gs_getspacesdir)}
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1
	local space=$(gs_getspace)

 	echo $(cd "$spacesdir/$space" ; find . -maxdepth 2 -type d -name ".git" -exec dirname {} \; | xargs basename -a | sort)
}

alias mvs=gs_mvspace
function gs_mvspace() {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	local oldspace newspace
	case "$1" in
		'')
			echo "What's the new space name?"
			echo "usage: mvgs <new-name>"
			return 1
			;;
		'--ask')
			while true; do
				read -p "New space name? " newspace
				case $newspace in
					'') continue ;;
					*)  break ;;
				esac
			done
			;;
		*)
			newspace=$1
			;;
	esac

	if [ -d "$spacesdir/$newspace" ]; then
		echo "space folder already exists: "$newspace
		return 1
	fi
	oldspace=$(gs_getspace)
	
	if [ "$oldspace" != "$newspace" ]; then
		cddir=$(pwd | sed "s/$oldspace/$newspace/")

		cd $spacesdir
		mv $oldspace $newspace
		cd $cddir
	fi

	return 0
}

# Manage sleeping (unused) environments
function gs_sleep() {
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	local lastz
	local nextz=1
	while test -d "$spacesdir/.zzz-$nextz"; do
	    (( ++nextz ))
	done
	lastz=$nextz
	(( --lastz )) # If 0 means no zzzs

	case "$1" in
		-c) # Return count of zzzs
			echo $lastz
			;;
		-n) # Echo the next one
			[ "$lastz" -gt 0 ] && echo .zzz-$lastz
			;;
		-w) # Wake one up
			if [ "$lastz" -eq 0 ]; then
				echo "Sorry. No more sleeping spaces."
			else
				gs_cdspace .zzz-$lastz
				gs_mvspace --ask
			fi
			;;
		*) # Default action: Put one to sleep
			if [[ "x$(gs_getspace)" == x.zzz* ]]; then
				echo "This is already a zzz space. Doing nothing."
				return 1
			else
				gs_mvspace .zzz-$nextz
				# Where to go next? (dont stay in this one)
				if [ $? -eq 0 ]; then
					# Can only get here if I'm in a repos
					local repos=$(basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null)
					gs_cdspace - $repos
				fi
			fi
			;;
	esac
}

#==
# CD Functions and Aliases
#==

# usage gs_cdspace [space|-] [repos] [/path|relpath]
#  usage: gs_cdspace -                     # select space to cd into
#  usage: gs_cdspace space                 # cd into alternate space, same directory if exists, otherwise top level
#  usage: gs_cdspace repos [/path|relpath] # cd into other repos to /path or relpath
#  usage: gs_cdspace [/path|relpath]       # standard cd except /path starts from root of current repos
# this function is never called by itself.
function gs_cdspace()  { 
	if [ $# -gt 3 ]; then
		>&2 echo "usage: gs_cdspace [space|-] [repos] [/path|relpath]"
		return 1
	fi
	
	local spacesdir=$(gs_getspacesdir)
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

	local space repos repospwd cdpath 
	[ $# -eq 1 ] && onlypath=true || onlypath=false

	# Get current or specified space
	space=$(gs_getspace $1)
	if [ $? -eq 1 ]; then
		shift # used $1 for space
	fi

	# Get target repos, if specified
	if [ $# -ge 1 ]; then
		local checkrepos
		for checkrepos in $1 $(gs_config get ReposAliases $1); do
			if [ "1" -eq $(find $spacesdir/$space -maxdepth 1 -type d -name "$checkrepos" 2> /dev/null | wc -l) ]; then
				repos=$checkrepos
				shift
				break
			fi
		done
	fi

	# If no repos set yet, take the current one, if we're in a repos
	[[ -z "$repos" ]] && repos=$(basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null)
	if [ -z "$repos" ]; then
		if [ $(cd "$spacesdir/$space" && gs_lsrepos | wc -w) -eq 1 ]; then
			repos=$(cd "$spacesdir/$space" && gs_lsrepos)
		else
			while [ "x$repos" == "x" ]; do
				PS3="Select repo: "
				select repos in $(cd "$spacesdir/$space" && gs_lsrepos); do break; done
			done
		fi
	fi

	repospwd=$(git rev-parse --show-prefix 2>/dev/null)
	cdpath=$1 # if any
	cd "$spacesdir/$space/$repos/$cdpath" 2> /dev/null              # relative to repos root
	if [ $? -ne 0 ]; then
		cd "$spacesdir/$space/$repos/$repospwd/$cdpath" 2> /dev/null  # relative to currdir
		if [ $? -ne 0 ]; then
			cd "$spacesdir/$space/$repos"                               # default to repos root
		fi
	fi

	if [[ "$space" == .zzz* ]]; then
		echo "You are waking a sleeping space."
		gs_mvspace --ask
	fi
}
