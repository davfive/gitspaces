/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/davfive/gitspaces/v2/console"
	"github.com/davfive/gitspaces/v2/gitspaces"

	"github.com/spf13/cobra"
)

// renameCmd represents the rename command
var renameCmd = &cobra.Command{
	Use:   "rename",
	Short: "Rename the current space",
	Long:  `Rename the current space`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		space, err := gitspaces.GetSpace()
		if err != nil {
			return err
		}

		if err = space.Rename(); err != nil {
			return console.Errorln("Failed to rename space: %s", err)
		}

		gitspaces.User.WriteCdToPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(renameCmd)
}
