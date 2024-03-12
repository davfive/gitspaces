package cmd

import (
	"github.com/davfive/gitspaces/v2/console"
	"github.com/davfive/gitspaces/v2/gitspaces"
	"github.com/davfive/gitspaces/v2/helper"

	"github.com/spf13/cobra"
)

// createCmd represents the create command
var createCmd = &cobra.Command{
	Use: UseWhere(
		"create [flags] <repo> [... <repo-N>] [<dir>]",
		[]WhereArg{
			{"repo", "repo as in `git clone <repo>`"},
			{"dir", "Directory to use for GitSpaces project. Default is first repo name."},
		},
	),
	Short:   "Creates a GitSpace from the provided repo url",
	Args:    cobra.MinimumNArgs(1),
	Aliases: []string{"c"},
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
