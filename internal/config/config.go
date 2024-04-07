package config

import (
	"github.com/spf13/cobra"
)

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
		User, err = initUser(ppidFlag)
	} else {
		User, err = initUser(-1)
	}
	return err
}

func ProjectPaths() []string {
	return User.projectPaths
}
