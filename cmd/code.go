package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/gitspaces"

	"github.com/spf13/cobra"
)

// codeCmd represents the code command
var codeCmd = &cobra.Command{
	Use:   "code",
	Short: "Open Space as a workspace in Visual Studio Code",
	Args:  cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		space, err := gitspaces.GetSpace()
		if err != nil {
			return err
		}

		if err = space.OpenVSCode(); err != nil {
			return console.Errorln("Failed to open Visual Studio Code: %s", err)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(codeCmd)
}
