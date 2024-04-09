package utils

import (
	"fmt"
	"os"
)

func ErrorIf(condition bool, message string) error {
	if condition {
		return fmt.Errorf("error: %s", message)
	}
	return nil
}

func PanicIfError(err error) {
	if err != nil {
		panic(fmt.Errorf("error: %w", err))
	}
}

func PanicIfFalse(condition bool, message string) {
	if !condition {
		panic(fmt.Errorf("error: %s", message))
	}
}

func PanicIfTrue(condition bool, message string) {
	if condition {
		panic(fmt.Errorf("error: %s", message))
	}
}

func PanicIfPathExists(path string) {
	_, err := os.Stat(path)
	PanicIfTrue(os.IsExist(err), "Directory already exists: "+path)
}

func PanicIfPathDoesNotExist(path string) {
	_, err := os.Stat(path)
	PanicIfFalse(os.IsExist(err), "Directory already exists: "+path)
}
