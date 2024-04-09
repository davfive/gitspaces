package console

import (
	"errors"
	"strings"

	"github.com/davfive/gitspaces/v2/internal/utils"
)

func MakeDirnameAvailableValidator(parentDir string) func(string) error {
	return func(dirname string) error {
		if strings.HasPrefix(dirname, ".") || utils.PathExists(utils.Join(parentDir, dirname)) {
			return errors.New("invalid")
		}
		return nil
	}
}
