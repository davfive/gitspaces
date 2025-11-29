# GitSpaces v3 - E2E Testing & Shell Integration Tasks

## Context
This is a Python port of the legacy Go implementation (https://github.com/davfive/gitspaces.golang). The core CLI functionality exists but lacks end-to-end tests and has behavioral differences from the legacy version that need to be fixed.

**Repository structure:**
- Python CLI: `src/gitspaces/` (entry: `cli.py`, commands: `modules/cmd_*.py`)
- Tests: `tests/` (unit tests exist, need E2E tests)
- Config location: `~/.gitspaces/config.yaml` (project directories list)
- Project marker: `__GITSPACES_PROJECT__` file in project root
- Sleeper clones: stored in `.zzz/` subdirectory with naming pattern `.zzz-N`

## Primary Objective
Create comprehensive end-to-end tests for all commands and fix behavioral discrepancies with the legacy implementation.

---

## Critical Issue: Shell Integration for `cd` Behavior

**Problem:** Python CLI cannot change the parent shell's directory. After `gitspaces switch`, user remains in original directory instead of switching to selected clone.

**Legacy Solution (Go version):** Used wrapper scripts (.sh/.cmd/.ps1) that:
1. CLI writes target directory to a PID-based file in `~/.gitspaces/`
2. Wrapper script reads file and executes `cd` in the shell
3. Cleans up PID file

**Required Actions:**
1. **Investigate:** Review legacy shell wrapper approach at https://github.com/davfive/gitspaces.golang
2. **Design:** Determine if we replicate the wrapper pattern or use alternative (shell functions, etc.)
3. **Implement:** Create shell integration for bash/zsh/fish/powershell
4. **Document:** Update README with installation/setup instructions for shell integration
5. **Test:** E2E tests must verify user ends up in correct directory after operations

**Affected Commands:** `switch`, `clone` (after creation), `rename` (after rename), `sleep` (when waking)

---

## E2E Test Requirements

### Test Framework
- Use pytest with temporary directories and real git repos
- Each test should create isolated config, project dirs, and git clones
- Use `conftest.py` fixtures for common setup (see existing patterns)
- Tests live in `tests/test_cmd_*_e2e.py` files

### Coverage Requirements
For each command, test:
1. **Happy path:** Normal successful execution
2. **Edge cases:** Empty states, max limits, invalid inputs
3. **Error handling:** Missing config, bad paths, git failures
4. **User interaction:** Menu selections, confirmations (use mocked input)
5. **State transitions:** Verify filesystem changes, config updates
6. **Output validation:** Check console messages match expected UX

---

## Command-Specific Fixes & Tests

### 1. `gitspaces switch` (alias: `gitspaces` with no args)

**Current Bugs:**
- **Bug 1.1:** When NOT in a gitspaces project → shows error "Not in a GitSpaces project directory"
  - **Expected:** Show list of ALL projects found under directories in config (scan for `__GITSPACES_PROJECT__` markers)
- **Bug 1.2:** Sleeper clones (`.zzz-*`) appear in selection list
  - **Expected:** Hide sleepers, show "Wake up (N)" option at bottom which prompts user for name and wakes one sleeper
- **Bug 1.3:** After selection → prints "Path: ..." but doesn't change directory
  - **Expected:** User's shell should cd into selected directory (requires shell integration)
- **Bug 1.4:** When selecting a sleeper directly → error "Cannot switch to sleeping space"
  - **Expected:** Prompt for name, wake it up, cd into it
- **Bug 1.5:** Current clone shows in selection list
  - **Expected:** Filter out current directory from list

**E2E Tests Needed:**
```python
# tests/test_cmd_switch_e2e.py

def test_switch_from_outside_project_shows_all_projects():
    """When not in any project, list all projects from config dirs"""
    
def test_switch_hides_sleeper_clones():
    """Sleeper .zzz-* clones should not appear in list"""
    
def test_switch_shows_wake_up_option_when_sleepers_exist():
    """Show 'Wake up (N)' option when N sleepers exist"""
    
def test_switch_filters_current_clone_from_list():
    """Current clone directory should not appear in selection"""
    
def test_switch_writes_target_path_for_shell_wrapper():
    """After selection, target path written to ~/.gitspaces/pid-{PID} file"""
    
def test_switch_wakes_sleeper_when_selected():
    """Selecting sleeper prompts for name and wakes it"""
```

### 2. `gitspaces clone <url>`

**Current Bugs:**
- **Bug 2.1:** Doesn't prompt user to select target directory from config
  - **Expected:** Show list of configured project directories, user picks one
- **Bug 2.2:** After creation, doesn't wake a sleeper and prompt for name
  - **Expected:** Automatically wake one sleeper, ask user for name, cd into it

**E2E Tests Needed:**
```python
# tests/test_cmd_clone_e2e.py

def test_clone_prompts_for_target_directory():
    """User selects from configured project directories"""
    
def test_clone_creates_project_structure():
    """Creates project dir with marker, main clone, and N sleepers in .zzz/"""
    
def test_clone_wakes_one_sleeper_after_creation():
    """After cloning, prompt user to name one sleeper and wake it"""
    
def test_clone_writes_path_for_shell_cd():
    """After waking sleeper, write path for shell wrapper to cd"""
```

### 3. `gitspaces code`

**Current Bugs:**
- **Bug 3.1:** Always shows selection list even when in a project clone
  - **Expected:** If in a clone directory, use that one by default (no prompt)
- **Bug 3.2:** Opens `code .` instead of workspace file
  - **Expected:** Open `.code-workspace/<project>~<clone>.code-workspace` file
  - Workspace files should be auto-generated/maintained per clone

**E2E Tests Needed:**
```python
# tests/test_cmd_code_e2e.py

def test_code_uses_current_clone_when_inside_project():
    """When in clone dir, open that clone without prompting"""
    
def test_code_creates_workspace_file():
    """Generate .code-workspace/<project>~<clone>.code-workspace if missing"""
    
def test_code_opens_workspace_not_folder():
    """Verify 'code' command receives .code-workspace file, not directory"""
    
def test_code_prompts_when_outside_project():
    """When not in project, show selection list of all clones"""
```

### 4. `gitspaces rename`

**Current Bugs:**
- **Bug 4.1:** Requires both old_name and new_name args
  - **Expected:** `gitspaces rename <new_name>` renames current clone directory
  - Should work when run from inside a clone (auto-detect old name)

**E2E Tests Needed:**
```python
# tests/test_cmd_rename_e2e.py

def test_rename_uses_current_clone_as_source():
    """When in clone dir, only require new_name argument"""
    
def test_rename_changes_directory_name():
    """Verify filesystem directory is renamed"""
    
def test_rename_updates_workspace_file():
    """Update .code-workspace/<project>~<new_name>.code-workspace"""
    
def test_rename_writes_new_path_for_shell_cd():
    """After rename, cd user into renamed directory"""
```

### 5. `gitspaces extend`

**Current Bugs:**
- **Bug 5.1:** Wrong help message at end
  - **Expected:** No follow-up message OR "Use 'gitspaces switch' to wake and name clones"
  - **Actual:** Says "Use 'gitspaces sleep' to wake..." (incorrect command)

**E2E Tests Needed:**
```python
# tests/test_cmd_extend_e2e.py

def test_extend_creates_new_sleeper_clone():
    """Verify new .zzz-N directory created with git clone"""
    
def test_extend_increments_sleeper_counter():
    """New sleeper gets next available number"""
    
def test_extend_outputs_correct_help_message():
    """Verify final message references 'gitspaces switch', not 'gitspaces sleep'"""
```

### 6. `gitspaces sleep`

**No reported bugs, but needs E2E tests:**

```python
# tests/test_cmd_sleep_e2e.py

def test_sleep_puts_active_clone_to_sleep():
    """Move clone dir to .zzz/ with next available number"""
    
def test_sleep_wakes_sleeper_with_new_name():
    """Select sleeper, prompt for name, move out of .zzz/"""
    
def test_sleep_list_shows_all_sleepers():
    """List command shows all .zzz-* directories"""
```

### 7. `gitspaces setup`

**E2E Tests Needed:**
```python
# tests/test_cmd_setup_e2e.py

def test_setup_creates_config_file():
    """Creates ~/.gitspaces/config.yaml with project_dirs"""
    
def test_setup_prompts_for_editor():
    """Allow user to configure default editor"""
    
def test_setup_validates_directory_paths():
    """Reject invalid/non-existent directories"""
```

---

## Implementation Checklist

### Phase 1: Shell Integration (Highest Priority)
- [ ] Research legacy wrapper scripts from golang repo
- [ ] Design Python equivalent or alternative approach
- [ ] Implement bash/zsh wrapper function or script
- [ ] Implement fish shell wrapper
- [ ] Implement PowerShell wrapper (Windows)
- [ ] Add installation instructions to README
- [ ] Test shell integration across platforms

### Phase 2: E2E Test Infrastructure
- [ ] Create `tests/conftest.py` fixtures for E2E tests:
  - Temporary config directory
  - Mock git repository factory
  - Project setup helper
  - Input/output capture utilities
- [ ] Set up test isolation (temp dirs, env vars)
- [ ] Add pytest markers for E2E vs unit tests

### Phase 3: Fix & Test Commands (by priority)
1. [ ] **switch** - Most critical, used constantly
2. [ ] **clone** - Entry point for new projects
3. [ ] **code** - Daily workflow
4. [ ] **rename** - Quality of life
5. [ ] **extend** - Low frequency, minor fix
6. [ ] **sleep** - Already working, just needs tests
7. [ ] **setup** - One-time use, low priority

### Phase 4: Documentation & CI
- [ ] Update README with shell integration setup
- [ ] Add E2E testing section to CONTRIBUTING.md
- [ ] Update CI workflows to run E2E tests
- [ ] Add troubleshooting guide for shell integration

---

## Testing Commands

Run E2E tests:
```bash
pytest tests/test_*_e2e.py -v
```

Run all tests:
```bash
pytest -v
```

Run specific command E2E tests:
```bash
pytest tests/test_cmd_switch_e2e.py -v
```

---

## Success Criteria

- [ ] All commands have comprehensive E2E test coverage (>80%)
- [ ] Shell integration works on bash, zsh, fish, PowerShell
- [ ] User can `cd` to selected/created/renamed directories automatically
- [ ] Sleeper clones properly hidden and wakeable via "Wake up" option
- [ ] `clone` command prompts for location and wakes first sleeper
- [ ] `code` command uses current clone and opens workspace files
- [ ] `rename` works with single argument from inside clone
- [ ] All E2E tests pass in CI
- [ ] Documentation updated with setup instructions