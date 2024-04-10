package config

import (
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

func RunUserEnvironmentChecks() bool {
	checksPassed := runUserEnvironmentChecks()
	if !checksPassed {
		runUserEnvironmentSetup(false)
	}
	return checksPassed
}

func RunUserEnvironmentSetup() {
	runUserEnvironmentSetup(true)
}

func runUserEnvironmentChecks() bool {
	return runConfigurationCheck() && runShellWrapperCheck()
}

func runConfigurationCheck() bool {
	return len(User.projectPaths) > 0
}

func runShellWrapperCheck() bool {
	return User.HasWrapId()
}

func runUserEnvironmentSetup(force bool) {
	console.Println("This will walk you through setting up GitSpaces.")
	if force {
		console.Println("It covers setting up some configuration and a shell wrapper.")
	}
	console.Println("See https://github.com/davfive/gitspaces README for full setup and use instructions.")
	console.Println("")

	runConfigurationSetup(force)
	shellUpdated := runShellWrapperSetup(force)

	console.Println("\nYou are ready to use GitSpaces (assuming you followed the instructions).")
	if shellUpdated {
		console.Println("Open a new shell and run 'gitspaces' (the shell wrapper) to start using GitSpaces.")
	} else {
		console.Println("Run 'gitspaces' (the shell wrapper) to start using GitSpaces.")
	}
}

// runProjectPathsCheck() prompts the user to set project paths in the config file
// if they are not already set. Returns true if user asked to update paths.
func runConfigurationSetup(force bool) bool {
	if !force && runConfigurationCheck() == true {
		return false
	}

	console.Println("= Project Paths Setup")
	console.Println("GitSpaces config.yaml file contains a ProjectPaths field.")
	console.Println("This field defines a list of paths to your project directories.")
	console.Println("")
	console.Println("The config.yaml file is located at: %s", User.GetConfigFile())
	console.Println("Instructions for setting up ProjectPaths field is in the config file.")
	console.Println("")

	if console.NewConfirm().Prompt("Edit config file now?").Run() == true {
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
func runShellWrapperSetup(force bool) bool {
	if !force && runShellWrapperCheck() == true {
		return false
	}

	console.Println("= Shell Wrapper Setup")
	console.Println("GitSpaces must be called using a lightweight shell wrapper function.")
	console.Println("The wrapper handles when a 'gitspaces <command>' needs to 'cd' to a new directory.")
	console.Println("")

	shellFiles := GetShellFiles()
	shellRcFile := User.getShellRcFile()
	shellName := User.GetTerminalType()
	askToEdit := false
	if User.pterm == "pwsh" {
		console.Println("Your PowerShell $PROFILE file: %s", shellRcFile)
		console.Println("\nPlease copy the following lines into the $PROFILE file:")
		console.Println(". %s", shellFiles["ps1ScriptBlock"].path)
		console.Println("Set-Alias -Name gs -Value gitspaces # optional")
		askToEdit = true
	} else {
		console.Println("Your current shell is: %s", utils.Ternary(shellName == "", "unknown", shellName))
		if shellName == "bash" || shellName == "zsh" {
			console.Println("Your shell profile/rc file: %s", shellRcFile)
			askToEdit = true
		}
		console.Println("\nPlease copy the following lines into your shell/rc file:")
		console.Println(". %s", shellFiles["shellFunction"].path)
		console.Println("alias gs=gitspaces")
	}

	if askToEdit {
		console.Println("")
		if console.NewConfirm().Prompt("Update %s now?", shellRcFile).Run() == true {
			utils.CreateEmptyFileIfNotExists(shellRcFile)
			if err := utils.OpenFileInDefaultApp(shellRcFile); err != nil {
				console.Errorln("%s", err)
			} else {
				console.NewInput().Prompt("Press <enter> when done editing the file ...").Run()
			}
		}
	}

	return true
}
