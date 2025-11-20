package config

import (
	_ "embed"
	"fmt"
	"os"
	"runtime"
	"slices"
	"strconv"
	"strings"
	"text/template"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"

	"github.com/spf13/viper"
)

//go:embed templates/config.yaml.tmpl
var defaultConfigYaml []byte

type userStruct struct {
	config       *viper.Viper
	dotDir       string
	wrapId       int
	pterm        string // Parent os stdout type (uname -o/-s)
	projectPaths []string
}

func (user *userStruct) GetConfigFile() string {
	return user.config.ConfigFileUsed()
}

func (user *userStruct) GetTerminalType() string {
	return user.pterm
}

func GetUserDotDir() string {
	return utils.Join(utils.GetUserHomeDir(), GsDotDir)
}

func (user *userStruct) SetParentProperties(wrapId int) {
	user.wrapId = wrapId // 0 = Debug (vscode launcher) mode
	user.pterm = utils.GetTerminalType()
}

func (user *userStruct) HasWrapId() bool {
	return user.wrapId >= 0
}

func (user *userStruct) WriteChdirPath(newdir string) {
	if user.wrapId <= 0 {
		return
	}
	notePath := utils.Join(user.dotDir, "chdir."+strconv.Itoa(user.wrapId))
	if err := os.WriteFile(notePath, []byte(newdir), os.FileMode(0o644)); err != nil {
		console.Errorln("auto chdir failed. cd to %s", newdir)
	}
}

func initUser(wrapIdFlag int) (user *userStruct, err error) {
	user = &userStruct{dotDir: GetUserDotDir()}
	user.SetParentProperties(wrapIdFlag)

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

func (user *userStruct) getTemplateVariables() map[string]interface{} {
	return map[string]interface{}{
		"exePath":    utils.Executable(),
		"homeDir":    utils.GetUserHomeDir(),
		"userDotDir": GetUserDotDir(),
	}
}

func (user *userStruct) getShellTmplVars(shellFiles map[string]*shellFileStruct) map[string]interface{} {
	tmplVars := user.getTemplateVariables()
	for _, shellFile := range shellFiles {
		tmplVars[shellFile.name+"Path"] = shellFile.path
	}

	return tmplVars
}

func (user *userStruct) checkProjectPaths() (err error) {
	configErrors := []string{}
	cleanedPaths := []string{}
	// An empty project paths file is handled by the RunUserEnvironmentChecks(), not here
	if len(user.projectPaths) > 0 {
		for _, path := range user.projectPaths {
			path = strings.TrimSpace(path)
			if path == "" {
				continue
			}

			if path, err = utils.Abs(path); err != nil {
				configErrors = append(configErrors, fmt.Sprintf("ProjectPath error: %s", err))
				continue
			}

			if !utils.PathExists(path) {
				configErrors = append(configErrors, fmt.Sprintf("ProjectPath does not exist: %s", path))
				continue
			}

			cleanedPaths = append(cleanedPaths, path)
		}
	}

	if len(configErrors) > 0 {
		console.Errorln("Config file errors: %s", user.config.ConfigFileUsed())
		for _, err := range configErrors {
			console.Errorln(err)
		}
		return fmt.Errorf("Config file errors")
	}

	user.projectPaths = cleanedPaths
	return nil
}

func (user *userStruct) getShellRcFile() string {
	if slices.Contains([]string{"bash", "zsh"}, user.pterm) {
		return utils.Join(utils.GetCygwinAwareHomeDir(), fmt.Sprintf(".%src", user.pterm))
	}

	if user.pterm == "pwsh" {
		// return os.Getenv("PROFILE") // For some reason this doesn't work (pwsh> $PROFILE)
		if runtime.GOOS == "windows" {
			return utils.Join(utils.GetUserHomeDir(), "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")
		} else {
			return utils.Join(utils.GetUserHomeDir(), ".config", "powershell", "Microsoft.PowerShell_profile.ps1")
		}
	}

	return ""
}

func (user *userStruct) initConfig() error {
	user.config = viper.New()
	user.config.SetConfigFile(utils.Join(user.dotDir, "config.yaml"))
	user.config.SetConfigType("yaml")
	if !utils.PathExists(user.config.ConfigFileUsed()) {
		user.writeDefaultConfig()
	}

	user.config.ReadInConfig()

	user.config.ReadInConfig()
	user.projectPaths = user.config.GetStringSlice("ProjectPaths")
	return user.checkProjectPaths()
}

func (user *userStruct) writeDefaultConfig() error {
	tmpl, err := template.New("config").Parse(string(defaultConfigYaml))
	if err != nil {
		return err
	}

	return utils.WriteTemplateToFile(tmpl, user.config.ConfigFileUsed(), user.getTemplateVariables())
}
