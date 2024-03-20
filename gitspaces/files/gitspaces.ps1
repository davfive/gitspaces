$gobin = (& go env GOPATH | Out-String) + "/bin"
& $gobin/gitspaces --ppid $PID $args
$gsExitCode=$LASTEXITCODE

if ($gsExitCode -eq 0) {
    $chdirFile=$HOME + "/.gitspaces/chdir." + $PID
    if ($chdirFile -and (Test-Path $chdirFile)) {
        $chdir=Get-Content -Path $chdirFile
        if ($chdir) {
            Set-Location $chdir
        }
        Remove-Item $chdir
    }
}
Exit $gsExitCode
