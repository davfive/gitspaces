#!/usr/bin/env bash
#------------------------------------------------------------
VERSION=`git describe --long --tags --dirty`
if [ $? -ne 0 -o -z "${VERSION}" ]; then
    echo "Failed to get version from 'git describe --long --tags --dirty'"
    exit 1
fi
GOFLAGS=-ldflags=-X=main.Version=$VERSION
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
        echo "Cannot publish tag with later commits: $VERSION"
        echo "Please create/push a new tag"
        exit 1
    fi
}

function gorun() {
    (set -x; GOFLAGS="$GOFLAGS" go "$@")
}

case "$1" in
    "build")
        gorun build -o build/gitspaces
        ;;
    "install")
        gorun install
        ;;
    "publish")
        check_version
        GOPROXY=proxy.golang.org gorun list -m github.com/davfive/gitspaces/v2@$VERSION
        exit 1
        ;;
    *)
        echo "Usage: $0 {build|install|publish}"
        exit 1
        ;;
esac
