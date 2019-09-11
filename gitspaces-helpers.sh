function gs_askyesno {
	local yn
	retcode=1
	while true; do
		read -n 1 -p "$1? [y/n] " yn
		case $yn in
		  [Yy]) retcode=0; break;;
		  [Nn]) retcode=1; break;;
		esac
		echo
	done
	echo
	return $retcode
}

export GS_ECHO_BLUE='\033[34m'
export GS_ECHO_GREEN='\033[32m'
export GS_ECHO_RED='\033[31m'
export GS_ECHO_PLAIN='\033[0m'
function gs_echoc() { local begcolor=$1; shift; echo -n -e $begcolor; echo -e "$@"$ECHO_PLAIN; }
function ts_tsecho() {	echo; gs_echoc $ECHO_BLUE "## `date +"%Y-%m-%d %H:%M:%S"`: ""$@"; }
