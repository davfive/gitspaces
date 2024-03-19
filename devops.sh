#!/usr/bin/env bash

LDFLAGS="-X main.Version=$version"

case "$1" in
    "build")
        version=`git describe --long --tags --dirty`
        (set -x; go build -ldflags "-X main.Version=$version" -o build/gitspaces)
        ;;
    "install")
        version=`git describe --long --tags --dirty`
        (set -x; go install -ldflags "-X main.Version=$version")
        ;;
    "publish")
        version=`git describe --long --tags --dirty 2>/dev/null`
        if [ $? -ne 0 ]; then
            echo "Failed to get version from 'git describe --long --tags --dirty'"
            exit 1
        elif [[ "$version" = *-dirty ]]; then
            echo "Cannot publish with modified (dirty) working directory: "$version
            echo "Please commit or stash your changes"
            exit 1
        elif ! [[ "$version" = *-0-* ]]; then
            echo "Cannot publish tag with later commits: "$version
            echo "Please create/push a new tag"
            exit 1
        fi
        
        echo GOPROXY=proxy.golang.org go list -m github.com/davfive/gitspaces/v2@ -ldflags \"-X main.Version=$version\"
        exit 1
        ;;
    *)
        echo "Usage: $0 {build|install|publish}"
        exit 1
        ;;
esac
