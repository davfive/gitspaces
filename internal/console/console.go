package console

import (
	"fmt"
	"os"
)

func Println(format string, a ...any) {
	fmt.Printf(format, a...)
	fmt.Println()
}

func Errorln(format string, a ...any) error {
	format = "Error: " + format
	fmt.Fprintf(os.Stderr, format, a...)
	fmt.Fprintln(os.Stderr)
	return fmt.Errorf(format, a...)
}
