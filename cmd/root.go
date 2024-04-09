package cmd

import (
	"os"
	"slices"

	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
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
	SilenceUsage:  true, // handle these below in Execute() call
	SilenceErrors: true,
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		debug, _ := cmd.Flags().GetBool("debug")
		if debug {
			console.Println("%v", os.Args)
		}

		if err := config.Init(cmd); err != nil {
			return err
		}

		if config.RunUserEnvironmentChecks() == true {
			os.Exit(1) // User asked to update environment.
		}
		return nil
	},
}

func Execute() {
	rootCmd.Root().CompletionOptions.DisableDefaultCmd = true
	rootCmd.PersistentFlags().Int("ppid", -1, "path to parent pid for communication")
	rootCmd.PersistentFlags().MarkHidden("ppid")
	rootCmd.PersistentFlags().String("pterm", "", "parent terminal type. Used for prompt support and setup instructions.")
	rootCmd.PersistentFlags().MarkHidden("pterm")
	rootCmd.PersistentFlags().BoolP("debug", "d", false, "Add additional debugging information")
	rootCmd.PersistentFlags().MarkHidden("debug")

	setDefaultCommandIfNonePresent()
	if cmd, err := rootCmd.ExecuteC(); err != nil {
		skipErrors := []string{"user aborted"}
		if !slices.Contains(skipErrors, err.Error()) {
			utils.PanicIfFalse(rootCmd.SilenceErrors, "SilenceErrors required for alternate error messaging")
			utils.PanicIfFalse(rootCmd.SilenceUsage, "SilenceUsage required for alternate error messaging")
			cmd.PrintErrln(cmd.ErrPrefix(), err.Error())
			cmd.PrintErrf("Run '%v -h' for usage.\n", cmd.CommandPath())
		}
		os.Exit(1)
	}
}

func SetVersion(version string) {
	if Version == "" {
		rootCmd.Version = version
	}
}

func flagsContain(flags []string, contains ...string) bool {
	for _, flag := range contains {
		if slices.Contains(flags, flag) {
			return true
		}
	}
	return false
}

func prefetchCommandAndFlags() (*cobra.Command, []string, error) {
	// Taken from cobra source code in command.go::ExecuteC()
	var cmd *cobra.Command
	var err error
	var flags []string
	if rootCmd.TraverseChildren {
		cmd, flags, err = rootCmd.Traverse(os.Args[1:])
	} else {
		cmd, flags, err = rootCmd.Find(os.Args[1:])
	}

	return cmd, flags, err
}

func setDefaultCommandIfNonePresent() {
	cmd, flags, err := prefetchCommandAndFlags()
	if err != nil || cmd.Use == rootCmd.Use {
		if !flagsContain(flags, "-v", "-h", "--version", "--help") {
			// Run w/o commands, default to switching projects/spaces
			rootCmd.SetArgs(append(os.Args[1:], "switch"))
		}
	}
}
