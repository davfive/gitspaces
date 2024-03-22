package helper

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

func GetIndex[S ~[]E, E any](s S, index int, fallback E) E {
	if index < len(s) {
		return s[index]
	}
	return fallback
}

func MakeDirnameAvailableValidator(parentDir string) func(string) error {
	return func(dirname string) error {
		if strings.HasPrefix(dirname, ".") || PathExists(filepath.Join(parentDir, dirname)) {
			return errors.New("invalid")
		}
		return nil
	}
}

func Executable() (exe string) {
	var err error

	if exe, err = os.Executable(); err == nil {
		if exe, err = filepath.EvalSymlinks(exe); err == nil {
			return exe
		}
	}
	return os.Args[0]
}
