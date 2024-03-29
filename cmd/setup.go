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
	Short: "Run gitspaces initial seteup",
	Long: `Run gitspaces initial seteup
- Create ~/.gitspaces directory
- Create ~/.gitspaces/config.yaml file
- Create ~/.gitspaces/gitspaces*.sh/.ps1 wrapper scripts
- Walk user through setting up envorinment.`,
	Run: func(cmd *cobra.Command, args []string) {
		config.Setup()
	},
}

func init() {
	rootCmd.AddCommand(setupCmd)
}
