#!/usr/bin/env bash
#------------------------------------------------------------
VERSION=`git describe --long --tags --dirty 2>/dev/null`
VERSION_SHORT=`git describe --tags --abbrev=0 2>/dev/null`
if [ -z "${VERSION}" -o -z "${VERSION_SHORT}" ]; then
    echo "Failed to get version from 'git describe --long --tags --dirty'"
    exit 1
fi
PACKAGE=github.com/davfive/gitspaces/v2
GOFLAGS=-ldflags=-X=$PACKAGE/cmd.Version=$VERSION
#=-----------------------------------------------------------

function check_version() {
    local branch=$(git branch --show-current)
    local majver=$(echo $VERSION | cut -d. -f1)

    if [ "$branch" != "$majver" ]; then
        echo "Cannot publish $VERSION from branch $branch"
        echo "Please check $VERSION version release branch: $majver"
        exit 1
    elif [[ "$VERSION" = *-dirty ]]; then
        echo "Cannot publish with modified (dirty) working directory: $VERSION"
        echo "Please commit or stash your changes"
        exit 1
    elif ! [[ "$VERSION" = *-0-* ]]; then
        # TODO: auto-create next tag when publishing new release
        echo "Cannot publish tag with later commits: $VERSION"
        echo "Please create/push a new tag"
        exit 1
    fi
}

case "$1" in
    "build")
        (set -x; go build $GOFLAGS -o build/gitspaces)
        ;;
    "install")
        (set -x; go install $GOFLAGS)
        ;;
    "publish")
        check_version
        (set -x; GOPROXY=proxy.golang.org go list -m $GOFLAGS $PACKAGE@$VERSION_SHORT)
        exit 1
        ;;
    *)
        echo "Usage: $0 {build|install|publish}"
        exit 1
        ;;
esac
