new-module -scriptblock {
    function gitspaces {
        . {{ .ps1ScriptPath }}
        return $LASTEXITCODE
    }
} -name gitspaces-scriptblock -force -export

