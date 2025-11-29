# GitSpaces shell wrapper for fish
# This wrapper enables cd behavior after gitspaces commands
#
# Installation:
#   Add to your ~/.config/fish/config.fish:
#     source /path/to/gitspaces/shell/gitspaces.fish
#
# Usage:
#   gs [command] [args...]
#   gitspaces [command] [args...]

function gs --description "GitSpaces CLI wrapper"
    # Run gitspaces with current shell PID
    command gitspaces $argv
    set -l exit_code $status

    # Check for shell target file
    set -l pid_file "$HOME/.gitspaces/pid-%self"
    if test -f "$pid_file"
        set -l target_dir (cat "$pid_file")
        rm -f "$pid_file"
        
        if test -d "$target_dir"
            cd "$target_dir"
        end
    end

    return $exit_code
end

# Alias gitspaces to gs function
alias gitspaces='gs'
