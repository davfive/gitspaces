/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/gitspaces"
	"github.com/spf13/cobra"
)

// renameCmd represents the rename command
var renameCmd = &cobra.Command{
	Use: UseWhere(
		"rename [flags] [<new-name>]",
		[]WhereArg{
			{"new-name", "name of the new space"},
		},
	),
	Short:   "Rename the current space",
	Args:    cobra.RangeArgs(0, 1),
	Aliases: []string{"move", "mv"},
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		space, err := gitspaces.GetSpace()
		if err != nil {
			return err
		}

		if err = space.Rename(args...); err != nil {
			return console.Errorln("Failed to rename space: %s", err)
		}

		console.Println("\nGitSpace renamed. Reopen any open IDEs from the new path")
		console.Println("or files saved in the IDE will save to the old GitSpace path.")
		config.User.WriteChdirPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(renameCmd)
}
