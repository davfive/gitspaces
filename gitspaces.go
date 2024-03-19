package main

import (
	cmd "github.com/davfive/gitspaces/v2/cmd"
)

// -ldflags "-X cmd.X=..." Build Flags
var Version string

func main() {
	cmd.SetVersion(Version)
	cmd.Execute()
}
