#!/usr/bin/env bash
function gitspaces() {
	$(go env GOPATH)/bin/gitspaces --ppid $$ "$@"
	cdtofile=~/.gitspaces/cdto.$$
	if [ -f $cdtofile ]; then
		[ $? -eq 0 ] && cd $(cat $cdtofile)
		rm -f $cdtofile
	fi
}