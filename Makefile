PACKAGE=github.com/davfive/gitspaces/v2
GOFLAGS=-ldflags=-X=${PACKAGE}/cmd.Version=${VERSION}
VERSION:=$(shell git describe --long --tags --dirty)
VERSION_SHORT:=$(shell git describe --tags --abbrev=0)
BRANCH:=$(shell git branch --show-current)
MAJVER:=$(shell echo ${VERSION} | cut -d. -f1)
#=-----------------------------------------------------------
.PHONY: checkbranch checkdirty checkpending checkversion
.PHONY: checkbuild checkinstall checkpublish
.PHONY: build install newtag publish
#=-----------------------------------------------------------
build: checkbuild
	@echo "[$@] Building ${VERSION} version"
	go build ${GOFLAGS} -o build/gitspaces

install: checkinstall build
	@echo "[$@] Installing ${VERSION} version"
	go install ${GOFLAGS}

newtag:
	@echo "[$@] Creating new tag for ${VERSION_SHORT} version"
	echo "$(tag)" | grep -qE "v2\.\d+\.\d+" # check tag format
	echo "{ \"version\": \"$(tag)\" }" > manifest.json
	git commit -am "Release $(tag)"
	git push
	git tag -a $(tag) -m "Release $(tag)"
	git push origin $(tag)

publish: checkpublish
	@echo "[$@] Publishing ${VERSION_SHORT} version"
	GOPROXY=proxy.golang.org go list -m ${GOFLAGS} ${PACKAGE}@${VERSION_SHORT}

#=-----------------------------------------------------------
checkbuild: checkversion
checkinstall: checkversion
checkpublish: checkversion checkbranch checkdirty checkpending
#=----------------------------------------------------------- 
checkbranch:
	@echo "[$@] Checking ${VERSION} version publish branch is ${MAJVER}"
	@if [ "${BRANCH}" != "${MAJVER}" ]; then \
		echo "Cannot publish ${VERSION} from branch ${BRANCH}"; \
		echo "Please check ${VERSION} version release branch: ${MAJVER}"; \
		exit 1; \
	fi

checkdirty:
	@echo "[$@] Checking working directory state"
	@if [[ "${VERSION}" = *-dirty ]]; then \
		echo "Cannot publish with modified (dirty) working directory: ${VERSION}"; \
		echo "Please commit or stash your changes"; \
		exit 1; \
	fi

checkpending:
	@echo "[$@] Checking that the tag is on the latest commit"
	@if ! [[ "${VERSION}" = *-0-* ]]; then \
		echo "Cannot publish tag with later commits: ${VERSION}"; \
		echo "Please create/push a new tag"; \
		exit 1; \
	fi

checkversion:
	@echo "[$@] Checking current git version: ${VERSION_SHORT} (${VERSION})"
	@if [ -z "${VERSION}" -o -z "${VERSION_SHORT}" ]; then \
		echo "Failed to get version from 'git describe --long --tags --dirty'"; \
		exit 1; \
	fi
 