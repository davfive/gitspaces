$cdToFile=$HOME + "/.gitspaces/cdto." + $PID
& gitspaces --ppid $PID $args
$gsExitCode=$LASTEXITCODE
if ($gsExitCode -eq 0) {
    if ($cdTofile -and (Test-Path $cdToFile)) {
        $cdToDir=Get-Content -Path $cdToFile
        if ($cdToDir) {
            Set-Location $cdToDir
        }
        Remove-Item $cdToFile
    }
}
Exit $gsExitCode