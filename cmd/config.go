package cmd

import (
	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/spf13/cobra"
)

// codeCmd represents the code command
var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Open GitSpaces config file (yaml) in default editor",
	Args:  cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		if err := config.User.OpenConfigFile(); err != nil {
			return console.Errorln("Failed to open GitSpaces config file:: %s", err)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
}
