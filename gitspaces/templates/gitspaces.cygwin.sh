#!/usr/bin/env bash
function gitspaces() {
	# Some bash terminals are not golang prompt package friendly (Cygwin/GitBash) for 
	uname=`uname -o`
	"{{ cygwinizePath .exePath }}" --ppid $$ "$@"
	chdirFile="{{ cygwinizePath .userDotDir }}/chdir.$$"
	if [ -f $chdirFile ]; then
		[ $? -eq 0 ] && cd $(cat $chdirFile)
		rm -f $chdirFile
	fi
}