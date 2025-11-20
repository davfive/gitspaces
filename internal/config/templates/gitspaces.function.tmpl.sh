function gitspaces() {
	local exePath="{{ .exePath }}"
	local dotDir="{{ .userDotDir }}"
	if echo "$(uname -s)" | grep -iq "CYGWIN"; then
		exePath="$(cygpath -m "$exePath")"
		dotDir="$(cygpath -m "$dotDir")"
	fi
	"$exePath" --wrapid $$ "$@"
	chdirFile="$dotDir/chdir.$$"
	if [ -f $chdirFile ]; then
		[ $? -eq 0 ] && cd $(cat $chdirFile)
		rm -f $chdirFile
	fi
}
