# GitSpaces Deployment Guide

## Overview

Deploy to PyPI via manual upload or automated GitHub Actions.

## Quick Reference

**Upload built packages from `dist/`, not source code:**
- `dist/gitspaces-*.whl` (wheel)
- `dist/gitspaces-*.tar.gz` (source distribution)

Build: `python -m build`

## Prerequisites

- Accounts on both PyPI and TestPyPI
- The package built locally (already done with `python -m build`)
- The `dist/` folder contains:
  - `gitspaces-2.0.36-py3-none-any.whl` (wheel file)
  - `gitspaces-2.0.36.tar.gz` (source tarball)

## Step 1: Create Accounts

### PyPI (Production)
1. Go to https://pypi.org/account/register/
2. Create your account and verify your email

### TestPyPI (Testing)
1. Go to https://test.pypi.org/account/register/
2. Create your account and verify your email

**Note:** These are separate accounts, so you need to register on both.

## Step 2: Reserve the Package Name

### Option A: Manual Upload (Recommended for First Time)

This is the easiest way to claim the name. You'll upload the **built package files** (not the source code repository) to PyPI.

**Important:** You're uploading the distribution packages from the `dist/` folder, NOT the git repository!

#### Step-by-Step Process:

1. **Build the package** (if not already done):
   ```bash
   cd /path/to/your/local/gitspaces/clone
   python -m build
   ```
   
   This creates two files in the `dist/` directory:
   - `gitspaces-2.0.36-py3-none-any.whl` (wheel file)
   - `gitspaces-2.0.36.tar.gz` (source distribution)

2. **Install twine** (if not already installed):
   ```bash
   pip install twine
   ```

3. **Upload to TestPyPI first** (to test before going to production):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   
   When prompted:
   - Username: Your TestPyPI username (or `__token__` if using API token)
   - Password: Your TestPyPI password (or paste your API token starting with `pypi-`)

4. **Test the TestPyPI installation**:
   ```bash
   # Create a test virtual environment
   python -m venv test-env
   source test-env/bin/activate  # On Windows: test-env\Scripts\activate
   
   # Install from TestPyPI
   pip install -i https://test.pypi.org/simple/ gitspaces
   
   # Test the command
   gitspaces --version
   
   # Clean up
   deactivate
   rm -rf test-env
   ```

5. **If TestPyPI works, upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```
   
   When prompted:
   - Username: Your PyPI username (or `__token__` if using API token)
   - Password: Your PyPI password (or paste your API token starting with `pypi-`)

**What gets uploaded:**
- The `.whl` file (wheel) - binary distribution
- The `.tar.gz` file (sdist) - source distribution
- NOT the git repository, NOT the source code directly

**What happens:**
- PyPI/TestPyPI stores these distribution files
- Users can install with `pip install gitspaces`
- pip downloads and installs from these distribution files

### Option B: Create API Tokens (Recommended for GitHub Actions)

Instead of using passwords, create API tokens:

#### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `github-actions-gitspaces`
4. Scope: Select "Entire account" (for first upload) or "Project: gitspaces" (after first upload)
5. Click "Add token"
6. **SAVE THE TOKEN** - you won't be able to see it again!

#### For PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `github-actions-gitspaces`
4. Scope: Select "Entire account" (for first upload) or "Project: gitspaces" (after first upload)
5. Click "Add token"
6. **SAVE THE TOKEN** - you won't be able to see it again!

## Step 3: Set Up GitHub Secrets

After creating your tokens, add them to your GitHub repository:

1. Go to your GitHub repository: https://github.com/davfive/gitspaces
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add two secrets:
   - Name: `PYPI_API_TOKEN`
     Value: Your PyPI API token (starts with `pypi-`)
   - Name: `TEST_PYPI_API_TOKEN`
     Value: Your TestPyPI API token (starts with `pypi-`)

## Step 4: Configure GitHub Environments

The workflow uses GitHub environments for approval gates. This must be configured in your **repository settings** (not user settings).

### Accessing GitHub Environments

1. Go to your repository: https://github.com/davfive/gitspaces
2. Click **"Settings"** (top right, repository settings, not user settings)
3. In the left sidebar, find the **"Environments"** section
4. Click **"New environment"** to create each environment

### Environment 1: TestPyPI (No Approval Needed)

**Configuration:**
- **Name**: `testpypi` (must match exactly as used in workflow)
- **Protection rules**: None needed (automatic deployment is fine for testing)
- **Environment secrets** (if using API tokens instead of Trusted Publishing):
  - Click "Add secret"
  - Name: `PYPI_API_TOKEN`
  - Value: Your TestPyPI API token

**What this does:**
- Allows automatic deployment to TestPyPI
- No manual approval required
- Used for testing before production

### Environment 2: PyPI (With Approval Gate)

**Configuration:**
- **Name**: `pypi` (must match exactly as used in workflow)
- **Protection rules**: 
  - ✅ Enable **"Required reviewers"**
  - Add reviewers: 
    - Add yourself: `@davfive`
    - Or add team members who can approve releases
  - Optionally set **"Wait timer"**: 0 minutes (or add delay if desired)
- **Environment secrets** (if using API tokens instead of Trusted Publishing):
  - Click "Add secret"
  - Name: `PYPI_API_TOKEN`
  - Value: Your PyPI API token

**What this does:**
- Requires manual approval before deploying to production PyPI
- Prevents accidental releases
- Creates a notification for reviewers to approve/reject

### Visual Guide to GitHub Environments Setup

```
GitHub Repository Settings
├── Settings (tab)
    ├── Secrets and variables
    │   └── Actions
    │       ├── Repository secrets (used by all workflows)
    │       │   ├── PYPI_API_TOKEN (optional if using Trusted Publishing)
    │       │   └── TEST_PYPI_API_TOKEN (optional if using Trusted Publishing)
    │       └── Environment secrets (used by specific environments)
    │
    └── Environments
        ├── testpypi
        │   ├── Protection rules: None
        │   └── Secrets: (none needed if using Trusted Publishing)
        │
        └── pypi
            ├── Protection rules:
            │   └── Required reviewers: [@davfive]
            └── Secrets: (none needed if using Trusted Publishing)
```

### Step-by-Step Environment Creation

#### Creating the `testpypi` Environment:

1. Go to: https://github.com/davfive/gitspaces/settings/environments
2. Click **"New environment"**
3. Enter name: `testpypi`
4. Click **"Configure environment"**
5. **Don't add any protection rules** (leave it open for automatic deployment)
6. Click **"Save protection rules"**
7. Done!

#### Creating the `pypi` Environment:

1. Go to: https://github.com/davfive/gitspaces/settings/environments
2. Click **"New environment"**
3. Enter name: `pypi`
4. Click **"Configure environment"**
5. **Add protection rules:**
   - Check ✅ **"Required reviewers"**
   - In the search box, type your username or team name
   - Select yourself: `davfive`
   - Click outside the box to confirm
6. Click **"Save protection rules"**
7. Done!

### How Approval Works

When you push a tag:

1. ✅ **Tests run** automatically
2. ✅ **Build completes** automatically  
3. ✅ **TestPyPI deployment** happens automatically
4. ⏸️ **GitHub creates an approval request** for PyPI environment
5. 📧 **You receive a notification** (email/GitHub)
6. 👀 **You review the deployment request** in GitHub Actions
7. ✅ **You click "Review deployments"** and approve/reject
8. ✅ **If approved, PyPI deployment** proceeds
9. ✅ **GitHub Release** is created with assets

### Verifying Environment Setup

After creating both environments, verify:

```bash
# Check your environments are configured
# Go to: https://github.com/davfive/gitspaces/settings/environments

# You should see:
# - testpypi (No protection rules)
# - pypi (Required reviewers: davfive)
```

### Common Issues

**"Environment not found" error in workflow:**
- Make sure environment names are exactly `testpypi` and `pypi` (lowercase, no spaces)
- Environments must be created before running the workflow

**"Approval not triggering":**
- Make sure you added yourself as a required reviewer in the `pypi` environment
- Check that you have the correct permissions (admin or maintainer)

**"Can't create environments":**
- Environments are only available on public repos, or private repos with GitHub Pro/Enterprise
- Make sure you're in the repository settings, not user settings

## Step 5: Test the Workflow

### Option 1: Use GitHub's Trusted Publishing (Recommended - No tokens needed!)

GitHub Actions now supports "Trusted Publishing" which is more secure than API tokens:

#### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add a new publisher:
   - PyPI Project Name: `gitspaces`
   - Owner: `davfive`
   - Repository: `gitspaces`
   - Workflow name: `python-publish.yml`
   - Environment name: `testpypi`

#### For PyPI:
1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - PyPI Project Name: `gitspaces`
   - Owner: `davfive`
   - Repository: `gitspaces`
   - Workflow name: `python-publish.yml`
   - Environment name: `pypi`

**Note:** For Trusted Publishing to work on the first upload, you might need to do one manual upload first to create the project.

### Option 2: Manual First Upload

If you prefer, do a manual upload first (see Step 2 Option A for detailed instructions):

```bash
# 1. Build the package distribution files
python -m build

# 2. Upload to TestPyPI first (test)
python -m twine upload --repository testpypi dist/*

# 3. Test install from TestPyPI
pip install -i https://test.pypi.org/simple/ gitspaces

# 4. If successful, upload to PyPI
python -m twine upload dist/*
```

**Remember:** You're uploading the built package files from `dist/`, not the git repository!

## Step 6: Trigger Automated Publishing

Once everything is set up:

1. Create a git tag with version:
   ```bash
   git tag -a v2.0.37 -m "Release v2.0.37"
   git push origin v2.0.37
   ```

2. The GitHub Actions workflow will:
   - ✅ Run all tests
   - ✅ Build the package
   - ✅ Extract version from tag
   - ✅ Publish to TestPyPI automatically
   - ⏸️ Wait for approval to publish to PyPI
   - ✅ Create GitHub Release with assets
   - ✅ Publish to PyPI after approval

## Verification

After publishing, verify your package:

### TestPyPI:
- View: https://test.pypi.org/project/gitspaces/
- Install test: `pip install -i https://test.pypi.org/simple/ gitspaces`

### PyPI:
- View: https://pypi.org/project/gitspaces/
- Install: `pip install gitspaces`

## Troubleshooting

### "Package name already taken"
If someone else has registered `gitspaces`, you'll need to choose a different name like `gitspaces-cli` or contact PyPI support.

### "Invalid credentials"
Make sure you're using the correct API token and that it hasn't expired.

### "Trusted Publishing not configured"
Do a manual upload first to create the project, then configure Trusted Publishing.

### "Version already exists"
You can't re-upload the same version. Increment the version number in:
- `pyproject.toml`
- `src/gitspaces/__init__.py`

## Recommended Approach

**First Time Setup:**
1. ✅ Create accounts on both platforms
2. ✅ Do ONE manual upload to TestPyPI to claim the name
3. ✅ Set up Trusted Publishing for both platforms
4. ✅ Configure GitHub environments
5. ✅ Push a new tag to test automated publishing

**For Future Releases:**
1. Update version in code
2. Create and push a tag
3. Approve the PyPI deployment when prompted
4. Done! 🎉

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR LOCAL REPOSITORY                             │
│                                                                      │
│  src/gitspaces/         ← Python source code                        │
│  tests/                 ← Test files                                │
│  pyproject.toml         ← Package metadata                          │
│  README.md              ← Documentation                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────┐              │
│  │ $ python -m build                                 │              │
│  │   (Creates distribution packages)                 │              │
│  └──────────────────────────────────────────────────┘              │
│                         │                                            │
│                         ▼                                            │
│  ┌──────────────────────────────────────────────────┐              │
│  │ dist/                                             │              │
│  │   ├── gitspaces-2.0.36-py3-none-any.whl          │ ◄─ UPLOAD    │
│  │   └── gitspaces-2.0.36.tar.gz                    │    THESE!    │
│  └──────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         │ $ twine upload --repository testpypi dist/*
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TEST.PYPI.ORG                                   │
│  (Testing environment - safe to experiment)                          │
│                                                                      │
│  Package: gitspaces                                                  │
│  Version: 2.0.36                                                     │
│  Files: .whl + .tar.gz stored on TestPyPI servers                  │
│                                                                      │
│  Users can install: pip install -i https://test.pypi.org/... gitspaces │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         │ (After testing works)
                         │ $ twine upload dist/*
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PYPI.ORG                                      │
│  (Production - the real deal!)                                       │
│                                                                      │
│  Package: gitspaces                                                  │
│  Version: 2.0.36                                                     │
│  Files: .whl + .tar.gz stored on PyPI servers                      │
│                                                                      │
│  Users can install: pip install gitspaces                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Current Package Status

The package has been built successfully:
- Source distribution: `dist/gitspaces-2.0.36.tar.gz`
- Wheel: `dist/gitspaces-2.0.36-py3-none-any.whl`

**These are the files you upload to PyPI/TestPyPI!**
