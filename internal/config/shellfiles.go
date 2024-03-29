package config

import (
	_ "embed"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"text/template"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

//go:embed templates/gitspaces.sh
var bashShellTmpl []byte

//go:embed templates/gitspaces.cygwin.sh
var cygwinShellTmpl []byte

//go:embed templates/gitspaces.ps1
var ps1Tmpl []byte

//go:embed templates/gitspaces.scriptblock.ps1
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
		"bashScript": NewShellFile("bashScript").
			File("gitspaces.sh").
			Template(string(bashShellTmpl)),
		"ps1Script": NewShellFile("ps1Script").
			File("gitspaces.ps1").
			Template(string(ps1Tmpl)),
		"ps1ScriptBlock": NewShellFile("ps1ScriptBlock").
			File("gitspaces.scriptblock.ps1").
			Template(string(ps1ScriptBlockTmpl)),
	}
	if runtime.GOOS == "windows" {
		shellFiles["cygwinScript"] = NewShellFile("cygwinScript").
			File("gitspaces.cygwin.sh").
			Template(string(cygwinShellTmpl))
	}
	return shellFiles
}

func (user *userStruct) updateShellFiles() bool {
	// TODO: Update only if first-run with new version of gitspaces (via config file)
	requiredUpdate := true
	shellFiles := GetShellFiles()
	tmplVars := map[string]interface{}{
		"exePath":    utils.Executable(),
		"userDotDir": user.dotDir,
	}
	for _, shellFile := range shellFiles {
		tmplVars[shellFile.name+"Path"] = shellFile.path
	}

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

func NewShellFile(name string) *shellFileStruct {
	return &shellFileStruct{
		name: name,
		dir:  GetUserDotDir(),
		path: "",
		tmpl: "",
		vars: map[string]interface{}{},
		funcs: template.FuncMap{
			"cygwinizePath": func(path string) string {
				driveRe := regexp.MustCompile("^(?P<drive>[A-z]+):")
				path = driveRe.ReplaceAllString(path, "/${drive}")
				path = strings.Replace(path, "\\", "/", -1)
				return path
			},
		},
	}
}

func (shellFile *shellFileStruct) File(file string) *shellFileStruct {
	shellFile.path = filepath.Join(shellFile.dir, file)
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
