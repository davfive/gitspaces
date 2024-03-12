package cmd

import (
	"os"

	"github.com/davfive/gitspaces/v2/gitspaces"
	"github.com/davfive/gitspaces/v2/helper"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:     "gitspaces",
	Short:   "Concurrent development manager for a single project",
	Version: helper.GetBuildVersion(),
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		return gitspaces.Init(cmd)
	},
}

func Execute() {
	rootCmd.Root().CompletionOptions.DisableDefaultCmd = true
	rootCmd.PersistentFlags().IntP("ppid", "", -1, "path to parent pid for communication")
	rootCmd.PersistentFlags().MarkHidden("ppid")
	setSwitchCommandAsDefault()
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func setSwitchCommandAsDefault() {
	switch len(os.Args[1:]) {
	case 0:
		rootCmd.SetArgs([]string{"switch"})
	case 2:
		if os.Args[1] == "--ppid" {
			// handle being called from the parent process with the ppid flag
			rootCmd.SetArgs(append(os.Args[1:], "switch"))
		}
	}
}
