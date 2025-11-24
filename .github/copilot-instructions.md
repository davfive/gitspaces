# Repository-wide Copilot Instructions — davfive/gitspaces

You are GitHub Copilot (@copilot) on github.com. Be concise. Prefer command snippets and exact copy/paste.

This file adapts the official GitHub "Repository-wide instructions" template to this repository. These rules apply repository-wide unless a more specific file or issue overrides them.

## Repository overview
This is a Go-based repository with a Ruby client for certain API endpoints. It is primarily responsible for ingesting metered usage for GitHub and recording that usage. See README.md for high-level details.

Quick facts
- Repository: davfive/gitspaces
- Primary languages: Go (service) and Ruby (client)
- Purpose: ingest and record metered usage for GitHub APIs

## Tone & agent expectations
- Short, exact, actionable responses. Prefer commands and copy/paste-ready file contents.
- Assume an experienced developer. Avoid explaining basic concepts.
- If you say you'll perform an action, do it in the same response or explain why you cannot.

## Agent session instructions (FOR COPILOT ONLY — NOT repository code rules)
These instructions are for Copilot during interactive sessions where the developer will copy/paste scripts or follow step-by-step commands. They are NOT repository policy and must not be presented as mandatory contributor requirements.

- Purpose: guide Copilot's chat output so the developer can copy/paste or run commands safely and consistently.
- Scope: Only applies to artifacts or command snippets produced in the interactive chat session.

### Before generating or proposing scripts in a session
- As guidance for session output (NOT repo policy), when preparing copy/paste-ready scripts or command sequences include a formatting step the user can run locally:
  - Because: ensure the developer receives consistently formatted snippets they can paste/run
  - Afterward: snippet is formatted
  - make fmt
  - (expects gofmt for Go; run Ruby formatters as needed)

### When producing bash scripts or runnable command sequences for the user
- Always include full file contents for scripts and start scripts with exactly:
  set -euxo pipefail
- Add minimal safety checks: fail on error and check target directories (fail if the target exists).
- Marker rules: When including the literal markers "Because:" and "Afterward:" inside code blocks or file blocks, prefix them with the language's single-line comment token so they remain comment lines in the code block (for example `# Because:` for bash/python, `// Because:` for Go/JS). Outside code blocks, use the plain labels Because: and Afterward: (no leading comment token). If a literal leading `#` is required in non-code text, escape it as `\#`.
- For each command section inside script file contents include (using the language-appropriate comment prefix):
  - Because: <why>
  - Afterward: <new state>
  - <commands>

Example (how to present a session-ready script snippet):
```bash name=scripts/session-install.sh url=https://github.com/davfive/gitspaces/blob/main/scripts/session-install.sh
set -euxo pipefail
# Because: ensure idempotent, safe installs for the user to run
# Afterward: dependencies installed in .venv
if [ -d .venv ]; then
  echo "target exists"; exit 1
fi
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Repository-level guidance (for contributors)
These are the actual repository expectations contributors should follow.

### Development flow
- Build: make build
- Test: make test
- Full CI check: make ci (includes build, fmt, lint, test)

### Tests & style
- Write unit tests for new functionality; prefer table-driven tests for Go.
- Document public APIs with godoc-style comments (Go) and YARD-style (Ruby) as appropriate.
- Keep changes small and focused; one logical change per PR.

## Repository structure
- cmd/: Main service entry points and executables
- internal/: Logic related to interactions with other GitHub services
- lib/: Core Go packages for billing logic
- admin/: Admin interface components
- config/: Configuration files and templates
- docs/: Documentation
- proto/: Protocol buffer definitions — run make proto after updates
- ruby/: Ruby implementation components — when updating, bump `ruby/lib/billing-platform/version.rb` using semantic versioning
- testing/: Test helpers and fixtures

## Key guidelines
1. Follow Go best practices and idiomatic patterns.
2. Maintain existing project structure; prefer dependency injection where appropriate.
3. Write unit tests for new behavior. Add integration tests when behavior spans multiple packages/services.
4. Use clear docstrings and update docs/ for user-facing changes.
5. Do not commit secrets; use GitHub Secrets for CI.

## CI & workflows
- Respect existing workflows under .github/workflows. Mirror CI steps locally when preparing changes.
- Keep CI green. If a change will temporarily break CI, explain why and provide a mitigation plan in the PR.

## Making changes — preferred workflow
- Create a short-lived feature branch.
- One logical change per PR with small commits.
- PR description must include:
  - What changed (concise)
  - Why it changed (brief)
  - How to test (exact commands)
  - Migration notes for API/behavior changes
- Include tests for behavioral changes; add docstrings for new exported functions.

## Scripts rules (repository guidance)
- When committing scripts into the repository, include full file contents and sensible safety checks.
- Committed scripts should begin with `set -euxo pipefail` and include checks as appropriate.
- When presenting committed script files in proposals, follow the file header format below.

## Files — how to propose new or changed files
- Always show complete file contents.
- When proposing a file from this repository, use a code block whose header includes `name=` and the GitHub permalink `url=`. Example:
```go name=lib/example.go url=https://github.com/davfive/gitspaces/blob/main/lib/example.go
package lib

// Example function
func Example() bool {
    return true
}
```
- For Markdown files, wrap the file block with four backticks so internal code blocks are preserved. Example:
````markdown name=docs/usage.md url=https://github.com/davfive/gitspaces/blob/main/docs/usage.md
