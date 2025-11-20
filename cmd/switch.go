/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/gitspaces"
	"github.com/spf13/cobra"
)

// switchCmd represents the switch command
var switchCmd = &cobra.Command{
	Use:   "switch",
	Short: "Switch to project/space (user choice)",
	Args:  cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		space, err := gitspaces.SwitchSpace()
		if err != nil {
			return err
		}

		config.User.WriteChdirPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(switchCmd)
}
