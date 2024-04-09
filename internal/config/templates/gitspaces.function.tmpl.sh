function gitspaces() {
	local exePath="{{ cygwinizePath .exePath }}"
	local dotDir="{{ cygwinizePath .userDotDir }}"
	"$exePath" --wrapid $$ "$@"
	chdirFile="$dotDir/chdir.$$"
	if [ -f $chdirFile ]; then
		[ $? -eq 0 ] && cd $(cat $chdirFile)
		rm -f $chdirFile
	fi
}
