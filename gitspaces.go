package main

import (
	_ "embed"
	"encoding/json"

	"github.com/davfive/gitspaces/v2/cmd"
)

//go:embed manifest.json
var manifestBytes []byte

type manifestStruct struct {
	Version string `json:"version"`
}

func main() {
	manifest := &manifestStruct{}
	json.Unmarshal(manifestBytes, manifest)
	cmd.SetVersion(manifest.Version)

	cmd.Execute()
}
