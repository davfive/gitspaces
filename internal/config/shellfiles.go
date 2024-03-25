package config

import (
	_ "embed"
	"os"
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

func (user *userStruct) updateShellFiles() bool {
	// TODO: Update only if first-run with new version of gitspaces (via config file)
	requiredUpdate := true
	shellFiles := []*shellFileStruct{
		user.NewShellFile("bashScript").
			File("gitspaces.sh").
			Template(string(bashShellTmpl)),
		user.NewShellFile("ps1Script").
			File("gitspaces.ps1").
			Template(string(ps1Tmpl)),
		user.NewShellFile("ps1ScriptBlock").
			File("gitspaces.scriptblock.ps1").
			Template(string(ps1ScriptBlockTmpl)),
	}
	if runtime.GOOS == "windows" {
		shellFiles = append(shellFiles,
			user.NewShellFile("cygwinScript").
				File("gitspaces.cygwin.sh").
				Template(string(cygwinShellTmpl)),
		)
	}

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

func (user *userStruct) NewShellFile(name string) *shellFileStruct {
	return &shellFileStruct{
		name: name,
		dir:  user.dotDir,
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

	var f *os.File
	if f, err = os.Create(shellFile.path); err != nil {
		return err
	}

	err = tmpl.Execute(f, shellFile.vars)
	f.Close()
	return err
}
