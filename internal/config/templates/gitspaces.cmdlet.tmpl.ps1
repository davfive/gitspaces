& "{{ .exePath }}" --wrapid $PID $args
$gsExitCode=$LASTEXITCODE

if ($gsExitCode -eq 0) {
    $chdirFile="{{ .userDotDir }}/chdir." + $PID
    if ($chdirFile -and (Test-Path $chdirFile)) {
        $chdir=Get-Content -Path $chdirFile
        if ($chdir) {
            Set-Location $chdir
        }
        Remove-Item $chdirFile
    }
}
Exit $gsExitCode
