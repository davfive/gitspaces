package cmd

import (
	"os"

	"github.com/davfive/gitspaces/v2/gitspaces"
	"github.com/spf13/cobra"
)

// Version string value (priority order)
// 1. -ldflags "-X cmd.X=..." Build Flags
// 2. //go:embed manifest.json (needed for go list publishing)
// 3. default value ""
var Version string = ""

var rootCmd = &cobra.Command{
	Use:           "gitspaces",
	Version:       Version,
	Short:         "Concurrent development manager for git projects",
	SilenceUsage:  true,
	SilenceErrors: true,
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		return gitspaces.Init(cmd)
	},
}

func Execute() {
	rootCmd.Root().CompletionOptions.DisableDefaultCmd = true
	rootCmd.PersistentFlags().Int("ppid", -1, "path to parent pid for communication")
	rootCmd.PersistentFlags().MarkHidden("ppid")
	rootCmd.PersistentFlags().String("pterm", "", "`uname -o` (parent terminal). Used for prompt support)")
	rootCmd.PersistentFlags().MarkHidden("pterm")

	setSwitchCommandAsDefault()
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func SetVersion(version string) {
	if Version == "" {
		rootCmd.Version = version
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
