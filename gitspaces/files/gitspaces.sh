#!/usr/bin/env bash
function gitspaces() {
	# Some bash terminals are not golang prompt package friendly (Cygwin/GitBash) for 
	uname=`uname -o`}
	$(go env GOPATH)/bin/gitspaces --ppid $$ --pterm "$uname" "$@"
	cdtofile=~/.gitspaces/cdto.$$
	if [ -f $cdtofile ]; then
		[ $? -eq 0 ] && cd $(cat $cdtofile)
		rm -f $cdtofile
	fi
}