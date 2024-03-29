package config

import (
	_ "embed"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
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
	ppid         int
	pterm        string // Parent os stdout type (uname -o/-s)
	projectPaths []string
}

func (user *userStruct) GetConfigFile() string {
	return user.config.ConfigFileUsed()
}

func GetUserDotDir() string {
	return filepath.Join(utils.GetUserHomeDir(), GsDotDir)
}

func Setup() {
	console.PrintSeparateln("Configuring GitSpaces for %s", utils.GetUserHomeDir())

	user, err := initUser()
	if err != nil {
		console.Errorln("User setup failed: %s", err)
		return
	}
	shellFiles := GetShellFiles()

	console.Println("GitSpaces generated configuration files:")
	console.Println("  %s", user.config.ConfigFileUsed())
	for _, key := range utils.SortKeys(shellFiles) {
		console.Println("  %s", shellFiles[key].path)
	}
	console.Println("")
	if console.NewConfirm().Prompt("Edit config file?").Run() == true {
		if err = utils.OpenFileInDefaultApp(user.GetConfigFile()); err != nil {
			console.Errorln("EditConfigFile failed: %s", err)
		}
	}
}

func initUser() (user *userStruct, err error) {
	user = &userStruct{
		dotDir: GetUserDotDir(),
		ppid:   -1,
	}

	for _, path := range []string{user.dotDir} {
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			return nil, err
		}
	}

	if err = user.initConfig(); err != nil {
		return nil, err
	}

	// ignore Update result (tells if updated or write errors - not fatal)
	user.updateShellFiles()

	return user, nil
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

func (user *userStruct) SetParentPid(ppid int) {
	if ppid > 0 {
		user.ppid = ppid
	}
}

func (user *userStruct) GetParentTerminal() string {
	return user.pterm
}

func (user *userStruct) SetParentTerminal(pterm string) {
	// from uname -o/-s (OS implementation for std output)
	if pterm != "" {
		user.pterm = pterm
	}
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
