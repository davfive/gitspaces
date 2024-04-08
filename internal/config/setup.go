package config

import (
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

// RunUserEnvironmentCheck() runs a series of checks to ensure the user's environment
// is properly configured for GitSpaces. Returns true if any checks failed.
// When a check fails, the user is prompted to update their environment. Once that is
// done, the user would be able to run the gitspaces command again successfully
func RunUserEnvironmentCheck() (checkFailed bool) {
	shellUpdated := false

	if runProjectPathsCheck() == true {
		checkFailed = true
	}
	if runShellWrapperCheck() == true {
		shellUpdated = true
		checkFailed = true
	}

	if checkFailed {
		console.Println("\nYou are ready to use GitSpaces (assuming you followed the instructions).")
		if shellUpdated {
			console.Println("Open a new shell and rerun 'gitspaces' (the shell wrapper) to start using GitSpaces.")
		} else {
			console.Println("Rerun 'gitspaces' (the shell wrapper) to start using GitSpaces.")
		}
	}
	return checkFailed
}

// runProjectPathsCheck() prompts the user to set project paths in the config file
// if they are not already set. Returns true if user asked to update paths.
func runProjectPathsCheck() bool {
	if len(User.projectPaths) > 0 {
		return false
	}

	console.Println("** Warning - Empty ProjectPaths found in %s **\n", User.GetConfigFile())
	console.Println("GitSpaces uses the ProjectPaths field to know where to find your projects")
	console.Println("Fill in the ProjectPaths in your config file with something like:")
	console.Println("ProjectPaths:")
	console.Println("  - {{.HomeDir}}/code/projects")
	console.Println("  - {{.HomeDir}}/code/play")
	console.Println("")

	if console.NewConfirm().Prompt("Edit config file?").Run() == true {
		if err := utils.OpenFileInDefaultApp(User.GetConfigFile()); err != nil {
			console.Errorln("Editing config file failed: %s", err)
		}
	}
	return true
}

// runProjectPathsCheck() prompts the user to set project paths in the config file
// if they are not already set. Returns true if user asked to update paths.
func runShellWrapperCheck() bool {
	if User.wrapped {
		return false
	}

	console.Println("** Warning - GitSpaces not run from shell wrapper **\n")
	console.Println("GitSpaces requires a wrapper function in your shell profile/rc file.")
	console.Println("The wrapper handles when a 'gitspaces <command>' needs to 'cd' to a new directory.")
	console.Println("\nWrappers are available for common shells (bash, zsh, pwsh).")
	console.Println("See https://github.com/davfive/gitspaces README for all setup instructions.")
	console.Println("")

	if Debug {
		shellFiles := GetShellFiles()
		console.Println("The following wrapper files were created:")
		for _, key := range utils.SortKeys(shellFiles) {
			console.Println("      %s", shellFiles[key].path)
		}
		console.Println("")
	}

	if User.pterm != "" {
		console.Println("Your current shell is: %s", User.pterm)
	}
	if console.NewConfirm().Prompt("Would you like to configure it now?").Run() == true {
		switch User.pterm {
		case "bash", "zsh":
			setupBashZshWrapper()
		case "pwsh":
			setupPwshWrapper()
		default:
			console.Println("Unable to determine your current shell rc file. Assuming *nix-style.")
			console.Println("Copy/paste these lines into your shell's rc file:")
			console.Println(". %s/gitspaces.sh", utils.CygwinizePath(User.dotDir))
			console.Println("alias gs=gitspaces")
		}
	}

	return true
}

func setupBashZshWrapper() {
	shellrc := User.getShellRcFile()
	console.Println("Copy/paste these lines into your shell's rc file:")
	console.Println(". %s/gitspaces.sh", utils.CygwinizePath(User.dotDir))
	console.Println("alias gs=gitspaces")
	console.Println("\nYour shell rc file is located at: %s", shellrc)
	if console.NewConfirm().Prompt("Edit shell rc file?").Run() == true {
		if err := utils.OpenFileInDefaultApp(shellrc); err != nil {
			console.Errorln("Editing shell rc file failed: %s", err)
		}
	}
}

func setupPwshWrapper() {
	shellFiles := GetShellFiles()
	shellrc := User.getShellRcFile()
	console.Println("Copy/paste these lines into your PowerShell $PROFILE file:")
	console.Println(". %s", shellFiles["ps1ScriptBlock"].path)
	console.Println("Set-Alias -Name gs -Value gitspaces # optional")
	console.Println("\nYour PowerShell profile is located at: %s", shellrc)
	// console.Println("For more information on your PowerShell profile, see https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.4#the-profile-variable")
	if console.NewConfirm().Prompt("Edit PowerShell $PROFILE?").Run() == true {
		if err := utils.OpenFileInDefaultApp(shellrc); err != nil {
			console.Errorln("Editing PowerShell $PROFILE failed: %s", err)
		}
	}
}
