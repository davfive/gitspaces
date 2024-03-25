new-module -scriptblock {
    function gitspaces {
        . {{ .ps1ScriptPath }} $args
    }
} -name gitspaces-scriptblock -force -export

