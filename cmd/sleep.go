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

// sleepCmd represents the sleep command
var sleepCmd = &cobra.Command{
	Use:   "sleep",
	Short: "Put this Space to sleep. Invites user to Wakeup a new Space.",
	Args:  cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		space, err := gitspaces.GetSpace()
		if err != nil {
			return console.Errorln("You're not in a GitSpace")
		}

		if err = space.Sleep(); err != nil {
			return console.Errorln("Failed to sleep space")
		}

		space, err = gitspaces.SwitchSpace()
		if err != nil {
			return console.Errorln("Failed to choose new space to use")
		}

		config.User.WriteChdirPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(sleepCmd)
}
