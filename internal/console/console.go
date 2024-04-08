package console

import (
	"fmt"
	"os"
)

var debug bool = false

func SetDebug(debugFlag bool) {
	debug = debugFlag
}

func Debugln(format string, a ...any) {
	if debug {
		Println(format, a...)
	}
}

func Println(format string, a ...any) {
	fmt.Printf(format, a...)
	fmt.Println()
}

func PrintSeparateln(format string, a ...any) {
	fmt.Println()
	fmt.Printf(format, a...)
	fmt.Println()
	fmt.Println()
}

func Errorln(format string, a ...any) error {
	format = "Error: " + format
	fmt.Fprintf(os.Stderr, format, a...)
	fmt.Fprintln(os.Stderr)
	return fmt.Errorf(format, a...)
}
