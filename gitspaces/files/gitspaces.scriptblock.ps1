new-module -scriptblock {
    function gitspaces {
        . $HOME/.gitspaces/gitspaces.ps1
        return $LASTEXITCODE
    }
} -name gitspaces-scriptblock -force -export

