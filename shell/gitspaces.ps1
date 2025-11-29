# GitSpaces shell wrapper for PowerShell
# This wrapper enables cd behavior after gitspaces commands
#
# Installation:
#   Add to your PowerShell profile ($PROFILE):
#     . /path/to/gitspaces/shell/gitspaces.ps1
#
# Usage:
#   gs [command] [args...]
#   gitspaces [command] [args...]

function Invoke-GitSpaces {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    # Run gitspaces with current shell PID
    & gitspaces.exe @Arguments
    $exitCode = $LASTEXITCODE

    # Check for shell target file
    $pidFile = Join-Path $env:USERPROFILE ".gitspaces\pid-$PID"
    if (Test-Path $pidFile) {
        $targetDir = Get-Content $pidFile -Raw
        $targetDir = $targetDir.Trim()
        Remove-Item $pidFile -Force

        if (Test-Path $targetDir -PathType Container) {
            Set-Location $targetDir
        }
    }

    exit $exitCode
}

# Set up aliases
Set-Alias -Name gs -Value Invoke-GitSpaces
Set-Alias -Name gitspaces -Value Invoke-GitSpaces
