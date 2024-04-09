new-module -scriptblock {
    function gitspaces {
        . {{ .ps1CmdletPath }} $args
    }
} -name gitspaces-scriptblock -force -export
