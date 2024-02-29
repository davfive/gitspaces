package cmd

import (
	"fmt"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/gitspaces"
	"github.com/davfive/gitspaces/v2/internal/helper"

	"github.com/spf13/cobra"
)

// createCmd represents the create command
var createCmd = &cobra.Command{
	Use:   "create [flags] URL [DIR]",
	Short: "Creates a GitSpace from the provided repo url",
	Long:  "Creates a GitSpace from the provided repo url.",
	Args: func(cmd *cobra.Command, args []string) error {
		if len(args) < 1 {
			return fmt.Errorf("requires a URL argument")
		}
		if len(args) > 2 {
			return fmt.Errorf("unexpected positional arguments after URL [DIR]")
		}
		return nil
	},
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		url := args[0]
		dir := helper.GetStringAtIndex(args, 1, "")
		numClones, _ := cmd.Flags().GetInt("num_clones")

		var project *gitspaces.ProjectStruct
		var space *gitspaces.SpaceStruct

		if project, err = gitspaces.CreateProject(url, dir, numClones); err != nil {
			return err
		}

		if space, err = project.WakeupSpace(); err != nil {
			return err
		}

		console.Println("\nCreated GitSpace at '%s' with %d clones", project.Path, numClones)

		gitspaces.User.WriteCdToPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(createCmd)
	createCmd.Flags().IntP("num_clones", "n", 3, "Number of sleeper clones to create")
}
