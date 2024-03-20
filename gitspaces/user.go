package gitspaces

import (
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"

	"github.com/davfive/gitspaces/v2/console"
	"github.com/davfive/gitspaces/v2/helper"

	"github.com/spf13/viper"
)

//go:embed files/gitspaces.sh
var bashShellFile []byte

//go:embed files/gitspaces.ps1
var ps1File []byte

type shellFileStruct struct {
	name  string
	path  string
	bytes []byte
}

type userStruct struct {
	config       *viper.Viper
	dotDir       string
	ppid         int
	projectPaths []string
	shellFiles   []shellFileStruct
}

func (user *userStruct) OpenConfigFile() (err error) {
	configFile := user.config.ConfigFileUsed()
	if configFile == "" {
		return fmt.Errorf("No config file found")
	}

	switch runtime.GOOS {
	case "windows":
		return exec.Command("cmd", "/c", configFile).Start()
	case "darwin":
		return exec.Command("open", configFile).Start()
	default:
		return fmt.Errorf("unsupported OS: %s", runtime.GOOS)
	}
}

func initUser() (user *userStruct, err error) {
	userHomeDir, err := os.UserHomeDir()
	if err != nil {
		return nil, err
	}

	user = &userStruct{
		dotDir: filepath.Join(userHomeDir, GsDotDir),
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

	return user, nil
}

func (user *userStruct) createShellFiles() error {
	user.shellFiles = []shellFileStruct{
		{
			name:  "bashrc",
			path:  filepath.Join(user.dotDir, "gitspaces.sh"),
			bytes: bashShellFile,
		},
		{
			name:  "ps1",
			path:  filepath.Join(user.dotDir, "gitspaces.ps1"),
			bytes: ps1File,
		},
	}
	for _, shellFile := range user.shellFiles {
		if helper.PathIsFile(shellFile.path) {
			continue
		}
		if err := os.WriteFile(shellFile.path, shellFile.bytes, os.FileMode(0o644)); err != nil {
			return err
		}
	}

	return nil
}

func (user *userStruct) initConfig() error {
	user.config = viper.New()
	user.config.SetConfigName("config.yaml")
	user.config.SetConfigType("yaml")
	user.config.AddConfigPath(user.dotDir)

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

			if !helper.PathExists(path) {
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

func (user *userStruct) WriteCdToPath(cdtopath string) {
	if user.ppid <= 0 {
		return
	}
	notePath := filepath.Join(user.dotDir, "cdto."+strconv.Itoa(user.ppid))
	if err := os.WriteFile(notePath, []byte(cdtopath), os.FileMode(0o644)); err != nil {
		console.Errorln("auto cd failed. cd to %s", cdtopath)
	}
}
