function gitspaces() {
	local exePath="{{ .exePath }}"
	local dotDir="{{ .userDotDir }}"
	if [ `uname -o` = "Cygwin" ]; then
		exePath="{{ cygwinizePath .exePath }}"
		dotDir="{{ cygwinizePath .userDotDir }}"
	fi
	"$exePath" --wrapid $$ "$@"
	chdirFile="$dotDir/chdir.$$"
	if [ -f $chdirFile ]; then
		[ $? -eq 0 ] && cd $(cat $chdirFile)
		rm -f $chdirFile
	fi
}
