package config

import (
	_ "embed"
	"text/template"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

//go:embed templates/gitspaces.function.tmpl.sh
var shellFunctionTmpl []byte

//go:embed templates/gitspaces.cmdlet.tmpl.ps1
var ps1CmdletTmpl []byte

//go:embed templates/gitspaces.scriptblock.tmpl.ps1
var ps1ScriptBlockTmpl []byte

type shellFileStruct struct {
	name  string
	dir   string
	path  string
	tmpl  string
	vars  map[string]interface{}
	funcs template.FuncMap
}

func GetShellFiles() map[string]*shellFileStruct {
	shellFiles := map[string]*shellFileStruct{
		"shellFunction": NewShellFile("shellFunction").
			File("gitspaces.function.sh").
			Template(string(shellFunctionTmpl)),
		"ps1Cmdlet": NewShellFile("ps1Cmdlet").
			File("gitspaces.cmdlet.ps1").
			Template(string(ps1CmdletTmpl)),
		"ps1ScriptBlock": NewShellFile("ps1ScriptBlock").
			File("gitspaces.scriptblock.ps1").
			Template(string(ps1ScriptBlockTmpl)),
	}
	return shellFiles
}

func NewShellFile(name string) *shellFileStruct {
	return &shellFileStruct{
		name: name,
		dir:  GetUserDotDir(),
		vars: map[string]interface{}{},
		funcs: template.FuncMap{
			"cygwinizePath": utils.CygwinizePath,
		},
	}
}

func (shellFile *shellFileStruct) File(file string) *shellFileStruct {
	shellFile.path = utils.Join(shellFile.dir, file)
	return shellFile
}

func (shellFile *shellFileStruct) Template(tmpl string) *shellFileStruct {
	shellFile.tmpl = tmpl
	return shellFile
}

func (shellFile *shellFileStruct) Vars(vars map[string]interface{}) *shellFileStruct {
	for k, v := range vars {
		shellFile.vars[k] = v
	}
	return shellFile
}

func (shellFile *shellFileStruct) Save() (err error) {
	tmpl, err := template.
		New(shellFile.name).
		Funcs(shellFile.funcs).
		Parse(shellFile.tmpl)
	if err != nil {
		return err
	}

	return utils.WriteTemplateToFile(tmpl, shellFile.path, shellFile.vars)
}

func (user *userStruct) updateShellFiles() bool {
	// TODO: Update only if first-run with new version of gitspaces (via config file)
	requiredUpdate := true
	shellFiles := GetShellFiles()
	tmplVars := user.getShellTmplVars(shellFiles)

	for _, shellFile := range shellFiles {
		shellFile.Vars(tmplVars)
		if err := shellFile.Save(); err != nil {
			console.Errorln("failed to save shell file: %s", shellFile.path)
			console.Errorln(err.Error())
			continue // not fatal, user just won't have shell file to use
		}
	}
	return requiredUpdate
}
