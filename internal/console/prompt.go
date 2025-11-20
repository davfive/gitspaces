package console

import "runtime"

// Windows (powershell, cygwin, git bash) aren't propertly
// supported with pretty prompts (promptui or huh)
// So we'll use raw reads for these "dumb" terminals
var usePrettyPrompts = runtime.GOOS != "windows"

func SetUsePrettyPrompts(promptStylePretty bool) {
	usePrettyPrompts = promptStylePretty
}
