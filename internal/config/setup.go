package config

import (
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

func ForceUserEnvironmentSetup() {
	console.Println("============================")
	console.Println("== GitSpaces Setup Wizard ==")
	console.Println("============================")
	runUserEnvironmentChecks(true)
}

func RunUserEnvironmentChecks() bool {
	return runUserEnvironmentChecks(false)
}

// runUserEnvironmentChecks() runs a series of checks to ensure the user's environment
// is properly configured for GitSpaces. Returns true if any checks failed.
// When a check fails, the user is prompted to update their environment. Once that is
// done, the user would be able to run the gitspaces command again successfully
func runUserEnvironmentChecks(force bool) (checkFailed bool) {
	shellUpdated := false

	if runProjectPathsCheck(force) == true {
		checkFailed = true
	}
	if runShellWrapperCheck(force) == true {
		shellUpdated = true
		checkFailed = true
	}

	if checkFailed {
		console.Println("\nSee https://github.com/davfive/gitspaces README for full setup and use instructions.")
		console.Println("You are ready to use GitSpaces (assuming you followed the instructions).")
		if shellUpdated {
			console.Println("Open a new shell and run 'gitspaces' (the shell wrapper) to start using GitSpaces.")
		} else {
			console.Println("Run 'gitspaces' (the shell wrapper) to start using GitSpaces.")
		}
	}
	return checkFailed
}

// runProjectPathsCheck() prompts the user to set project paths in the config file
// if they are not already set. Returns true if user asked to update paths.
func runProjectPathsCheck(force bool) bool {
	if !force && len(User.projectPaths) > 0 {
		return false
	}

	console.PrintSeparateln("== Setup GitSpaces ProjectPaths")
	console.Println("GitSpaces uses the ProjectPaths field to know where to find your projects.")
	console.Println("")
	console.Println("Fill in the ProjectPaths in the GitSpaces config file with something like:")
	console.Println("ProjectPaths:")
	console.Println("  - %s/code/projects", utils.GetUserHomeDir())
	console.Println("  - %s/code/play", utils.GetUserHomeDir())
	console.Println("")
	console.Println("The config file is located at: %s", User.GetConfigFile())
	console.Println("")

	if console.NewConfirm().Prompt("Edit config file?").Run() == true {
		if err := utils.OpenFileInDefaultApp(User.GetConfigFile()); err != nil {
			console.Errorln("Editing config file failed: %s", err)
		} else {
			console.NewInput().Prompt("Press <enter> when done editing the file ...").Run()
		}
	}
	return true
}

// runProjectPathsCheck() prompts the user to set project paths in the config file
// if they are not already set. Returns true if user asked to update paths.
func runShellWrapperCheck(force bool) bool {
	if !force && User.HasWrapId() {
		return false
	}

	console.PrintSeparateln("== Setup GitSpaces Shell Wrapper")
	console.Println("GitSpaces requires a wrapper function in your shell profile/rc file.")
	console.Println("The wrapper handles when a 'gitspaces <command>' needs to 'cd' to a new directory.")
	console.Println("")

	if !User.HasWrapId() {
		console.Println("** Warning - GitSpaces not run from shell wrapper **\n")
	}

	shellFiles := GetShellFiles()
	if Debug {
		console.Println("The following wrapper files were created:")
		for _, key := range utils.SortKeys(shellFiles) {
			console.Println("      %s", shellFiles[key].path)
		}
		console.Println("")
	}

	console.Println("Shell Wrapper Setup Instructions:")
	console.Println("1. Copy the following lines:")
	if User.pterm == "pwsh" {
		console.Println(". %s", shellFiles["ps1ScriptBlock"].path)
		console.Println("Set-Alias -Name gs -Value gitspaces # optional")
	} else {
		console.Println(". %s", shellFiles["shellFunction"].path)
		console.Println("alias gs=gitspaces")
	}
	console.Println("2. Paste the lines into your shell profile or rc file.")
	console.Println("3. Open a new shell and run 'gitspaces' to start using GitSpaces.")

	if User.pterm != "" {
		shellRcFile := User.getShellRcFile()
		console.Println("\nYour current shell is: %s", User.pterm)
		console.Println("Your shell profile/rc file is located at: %s", shellRcFile)
		console.Println("")
		if console.NewConfirm().Prompt("Edit %s?", shellRcFile).Run() == true {
			utils.CreateEmptyFileIfNotExists(shellRcFile)
			if err := utils.OpenFileInDefaultApp(shellRcFile); err != nil {
				console.Errorln("Editing shell rc file failed: %s", err)
			} else {
				console.NewInput().Prompt("Press <enter> when done editing the file ...").Run()
			}
		}
	}

	return true
}
