package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/gitspaces"
	"github.com/davfive/gitspaces/v2/internal/utils"
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
		dir := utils.GetIndex(args, 1, "")
		numClones, _ := cmd.Flags().GetInt("num_spaces")

		var project *gitspaces.ProjectStruct
		var space *gitspaces.SpaceStruct

		if project, err = gitspaces.CreateProject(dir, url, numClones); err != nil {
			return err
		}

		if space, err = project.WakeupSpace(); err != nil {
			return err
		}

		console.Println("\nCreated GitSpace project at '%s' with %d spaces", project.Path, numClones)

		config.User.WriteChdirPath(space.Path)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(createCmd)
	createCmd.Flags().IntP("num_spaces", "n", 3, "Number of spaces to create in project")
}
