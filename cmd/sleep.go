/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/davfive/gitspaces/internal/console"
	"github.com/davfive/gitspaces/internal/gitspaces"

	"github.com/spf13/cobra"
)

// sleepCmd represents the sleep command
var sleepCmd = &cobra.Command{
	Use:   "sleep",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
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

		gitspaces.User.WriteCdToPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(sleepCmd)
}
