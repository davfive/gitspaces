package config

import (
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
	var wrapId int
	if wrapId, err = cmd.Flags().GetInt("wrapid"); err != nil {
		wrapId = -1
	}

	_, err = initUser(wrapId)
	return err
}

func ProjectPaths() []string {
	return User.projectPaths
}
