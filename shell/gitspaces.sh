#!/bin/bash
# GitSpaces shell wrapper for bash/zsh
# This wrapper enables cd behavior after gitspaces commands
#
# Installation:
#   Add to your ~/.bashrc or ~/.zshrc:
#     source /path/to/gitspaces/shell/gitspaces.sh
#
# Usage:
#   gs [command] [args...]
#   gitspaces [command] [args...]

gs() {
    # Run gitspaces with current shell PID
    command gitspaces "$@"
    local exit_code=$?

    # Check for shell target file
    local pid_file="${HOME}/.gitspaces/pid-$$"
    if [[ -f "$pid_file" ]]; then
        local target_dir
        target_dir=$(cat "$pid_file")
        rm -f "$pid_file"
        
        if [[ -d "$target_dir" ]]; then
            cd "$target_dir" || return 1
        fi
    fi

    return $exit_code
}

# Alias gitspaces to gs function
alias gitspaces='gs'
