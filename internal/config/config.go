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
	if User, err = initUser(); err != nil {
		return err
	}
	ppid, _ := cmd.Flags().GetInt("ppid")
	if ppid > 0 {
		User.SetParentPid(ppid)
	}

	pterm, _ := cmd.Flags().GetString("pterm")
	if pterm != "" {
		User.SetParentTerminal(pterm)
	}

	return nil
}

func ProjectPaths() []string {
	return User.projectPaths
}
