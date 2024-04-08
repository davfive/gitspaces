package config

import (
	_ "embed"
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"strconv"
	"strings"
	"text/template"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"

	"github.com/mitchellh/go-ps"
	"github.com/spf13/viper"
)

//go:embed templates/config.yaml.tmpl
var defaultConfigYaml []byte

type userStruct struct {
	config       *viper.Viper
	dotDir       string
	ppid         int
	pterm        string // Parent os stdout type (uname -o/-s)
	wrapped      bool   // exe called from gitspaces wrapper
	projectPaths []string
}

func (user *userStruct) GetConfigFile() string {
	return user.config.ConfigFileUsed()
}

func GetUserDotDir() string {
	return filepath.Join(utils.GetUserHomeDir(), GsDotDir)
}

func Setup() {
	console.Println(`
** Setup Action 1/2
** Add ProjectPaths to %s

GitSpaces will use these paths to find your projects
`, User.config.ConfigFileUsed())

	if console.NewConfirm().Prompt("Edit config file?").Run() == true {
		if err := utils.OpenFileInDefaultApp(User.GetConfigFile()); err != nil {
			console.Errorln("Editing config file failed: %s", err)
		}
	}

	console.Println(`
** Setup Action 2/2
** Update shell profile for %s ...

GitSpaces requires a wrapper function in your shell profile/rc file because
some commands change the current working directory. The wrapper handles this.

The following wrapper files were created:`, User.pterm)
	shellFiles := GetShellFiles()
	for _, key := range utils.SortKeys(shellFiles) {
		console.Println("      %s", shellFiles[key].path)
	}

	shellrc := User.getShellRcFile()
	if User.pterm == "pwsh" {
		console.Println(`
Add the following lines to your PowerShell $PROFILE file:
. %s
Set-Alias -Name gs -Value gitspaces # optional

Your PowerShell profile is located at: %s
For more information on your PowerShell profile, see https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.4#the-profile-variable

`, shellFiles["ps1Script"].path, shellrc)
		if console.NewConfirm().Prompt("Edit PowerShell $PROFILE?").Run() == true {
			if err := utils.OpenFileInDefaultApp(shellrc); err != nil {
				console.Errorln("Editing PowerShell $PROFILE failed: %s", err)
			}
		}
	} else if shellrc != "" {
		console.Println(`
Add the following lines to your current shell rc file:
. %s/gitspaces.sh
alias gs=gitspaces

Your shell rc file is located at: %s", 
`, utils.CygwinizePath(User.dotDir), shellrc)
		if console.NewConfirm().Prompt("Edit shell rc file?").Run() == true {
			if err := utils.OpenFileInDefaultApp(shellrc); err != nil {
				console.Errorln("Editing shell rc file failed: %s", err)
			}
		}
	} else {
		console.Println(`
Unable to determine your current shell rc file. Assuming *nix-style, add")
the following lines to your shell rc file:
. %s/gitspaces.sh
alias gs=gitspaces
`, utils.CygwinizePath(User.dotDir))
	}
}

func initUser(ppidFlag int) (user *userStruct, err error) {
	user = &userStruct{dotDir: GetUserDotDir()}
	user.SetParentProperties(ppidFlag)

	if err := os.MkdirAll(user.dotDir, os.ModePerm); err != nil {
		return nil, err
	}

	if err = user.initConfig(); err != nil {
		return nil, err
	}

	// ignore Update result (tells if updated or write errors - not fatal)
	user.updateShellFiles()

	return user, nil
}

func (user *userStruct) getShellTmplVars(shellFiles map[string]*shellFileStruct) map[string]interface{} {
	tmplVars := map[string]interface{}{
		"exePath":    utils.Executable(),
		"userDotDir": user.dotDir,
	}
	for _, shellFile := range shellFiles {
		tmplVars[shellFile.name+"Path"] = shellFile.path
	}

	return tmplVars
}

func (user *userStruct) writeDefaultConfig() error {
	tmpl, err := template.New("config").Parse(string(defaultConfigYaml))
	if err != nil {
		return err
	}

	return utils.WriteTemplateToFile(tmpl, user.config.ConfigFileUsed(), map[string]interface{}{
		"HomeDir": utils.GetUserHomeDir(),
	})
}

func (user *userStruct) initConfig() error {
	user.config = viper.New()
	user.config.SetConfigFile(filepath.Join(user.dotDir, "config.yaml"))
	user.config.SetConfigType("yaml")
	if !utils.PathExists(user.config.ConfigFileUsed()) {
		user.writeDefaultConfig()
	}

	user.config.ReadInConfig()

	user.config.ReadInConfig()
	user.projectPaths = user.config.GetStringSlice("ProjectPaths")
	return user.checkProjectPaths()
}

func (user *userStruct) checkProjectPaths() (err error) {
	configErrors := []string{}
	if len(user.projectPaths) == 0 {
		configErrors = append(
			configErrors,
			fmt.Sprintf("No 'ProjectPaths' section in %s", user.config.ConfigFileUsed()),
		)
	} else {
		for i, path := range user.projectPaths {
			if path, err = filepath.Abs(path); err != nil {
				configErrors = append(configErrors, fmt.Sprintf("ProjectPath error: %s", err))
				continue
			}

			if !utils.PathExists(path) {
				configErrors = append(configErrors, fmt.Sprintf("ProjectPath does not exist: %s", path))
				continue
			}

			user.projectPaths[i] = path // Abs() path
		}
	}

	if len(configErrors) > 0 {
		console.Errorln("Config file errors: %s", user.config.ConfigFileUsed())
		for _, err := range configErrors {
			console.Errorln(err)
		}
		return fmt.Errorf("Config file errors")
	}

	return nil
}

func (user *userStruct) getShellRcFile() string {
	if slices.Contains([]string{"bash", "zsh"}, user.pterm) {
		return filepath.Join(utils.GetUserHomeDir(), fmt.Sprintf(".%src", user.pterm))
	}

	if user.pterm == "pwsh" {
		return os.Getenv("PROFILE")
	}

	return ""
}

func (user *userStruct) SetParentProperties(ppid int) {
	realppid := os.Getppid()
	if ppid > 0 && ppid == realppid {
		user.ppid = ppid
		user.wrapped = true
	} else {
		user.wrapped = false
		user.ppid = os.Getppid()
	}

	if parentps, _ := ps.FindProcess(user.ppid); parentps != nil {
		user.pterm = strings.ToLower(filepath.Base(parentps.Executable()))
	} else {
		console.Debugln("Parent process name not found. Continuing without knowing parent shell type.")
		user.pterm = ""
	}

	console.Debugln("Parent pid: %d", user.ppid)
	console.Debugln("Parent terminal: %s", user.pterm)
}

func (user *userStruct) GetParentTerminal() string {
	return user.pterm
}

func (user *userStruct) WriteChdirPath(newdir string) {
	if user.ppid <= 0 {
		return
	}
	notePath := filepath.Join(user.dotDir, "chdir."+strconv.Itoa(user.ppid))
	if err := os.WriteFile(notePath, []byte(newdir), os.FileMode(0o644)); err != nil {
		console.Errorln("auto chdir failed. cd to %s", newdir)
	}
}
