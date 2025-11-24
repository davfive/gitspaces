# Repository-wide Copilot Instructions

You are GitHub Copilot (@copilot) on github.com. Be concise. Prefer command snippets and exact copy/paste.

Purpose
- Provide repository-wide guidance for Copilot-style coding agents and human contributors. Keep guidance focused, actionable, and minimal.

Scope
- This file contains default project conventions and instructions the coding agent should follow for all tasks unless a specific file or issue overrides them.

Tone & Style
- Prefer concise, direct answers; prioritize exact commands, complete file contents, and small focused diffs.
- Use present tense; assume the reader is an experienced developer (25+ years).
- When describing steps, show exact commands and copy/paste-ready snippets.

Files
- When proposing a file, present it as a code block whose header includes name and, if from GitHub, the permalink URL. Example (TypeScript file):
```typescript name=filename.ts url=https://github.com/owner/repo/blob/main/filename.ts
export const example = true
```
- For Markdown files, wrap the file block with four backticks so internal code blocks are preserved. Example: see this file.

Scripts
- Always provide full file contents for scripts. Start scripts with exactly:
set -euxo pipefail
- Include minimal safety checks: fail on error and check target directories (fail if the target exists).
- Marker rules: When including the literal markers "Because:" and "Afterward:" inside code blocks or file blocks, prefix them with the language's single-line comment token so they remain comment lines in the code block (for example "# Because:" for bash/python, "// Because:" for Go/JS). Outside code blocks, use the plain labels Because: and Afterward: (no leading comment token). If a literal leading '#' is required in non-code text, escape it as '\#'.
- For each command section inside script file contents include (using the language-appropriate comment prefix):
  - Because: <why>
  - Afterward: <new state>
  - <commands>

Example script (bash):
```bash name=scripts/example.sh url=https://github.com/davfive/gitspaces/blob/main/scripts/example.sh
set -euxo pipefail
# Because: prevent accidental overwrites and stop on errors
# Afterward: a new directory created with example file
if [ -d ./out ]; then
  echo "target exists"; exit 1
fi
mkdir -p ./out
echo hello > ./out/hello.txt
```

Issues & PRs
- When listing GitHub issues or PRs, include the complete list returned by any tool call inside a code block with language `list` and header attribute type="issue" or type="pr". Never truncate or omit entries.

Behavior
- If you say you will perform an action, perform it in the same response or explain why you cannot.
- Keep replies short and provide exact commands or file blocks when relevant.

Examples & Preferences
- Prefer small self-contained changes and single-purpose commits.
- When proposing changes, include the exact file contents and the proposed permalink header syntax.
- Fail fast: prefer explicit checks at the top of scripts and clear error messages.

Contact
- For exceptions or repo-specific conventions not covered here, consult the repository owner or open an issue.
