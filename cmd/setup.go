/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/spf13/cobra"
)

// setupCmd represents the setup command
var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "(Re)run gitspaces setup wizard",
	Run: func(cmd *cobra.Command, args []string) {
		config.RunUserEnvironmentSetup()
	},
}

func init() {
	rootCmd.AddCommand(setupCmd)
}
