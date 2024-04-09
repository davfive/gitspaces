package config

import (
	"os"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/spf13/cobra"
)

var Debug bool = false

var User *userStruct

const (
	GsDotDir      = ".gitspaces"
	GsProjectFile = "__GITSPACES_PROJECT__"
	GsSleeperDir  = ".zzz"
	GsVsCodeWsDir = ".code-workspace"
)

func Init(cmd *cobra.Command) (err error) {
	var ppidFlag int
	if ppidFlag, err = cmd.Flags().GetInt("ppid"); err != nil {
		ppidFlag = -1
	}
	if ppidFlag == 0 { // 0 is the debugging pid to autoselect parent pid
		ppidFlag = os.Getppid()
	}

	User, err = initUser(ppidFlag)

	if debug, err := cmd.Flags().GetBool("debug"); err == nil {
		Debug = debug
		console.SetDebug(Debug)
	}

	return err
}

func ProjectPaths() []string {
	return User.projectPaths
}
