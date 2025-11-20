# PyPI Setup Guide for GitSpaces

This guide will help you reserve the `gitspaces` name on PyPI and TestPyPI, and set up automated publishing via GitHub Actions.

## Prerequisites

- Accounts on both PyPI and TestPyPI
- The package built locally (already done with `python -m build`)

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

This is the easiest way to claim the name:

#### For TestPyPI:
```bash
# Install twine if not already installed
pip install twine

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

When prompted:
- Username: Your TestPyPI username
- Password: Your TestPyPI password (or API token)

#### For PyPI:
```bash
# Upload to PyPI
python -m twine upload dist/*
```

When prompted:
- Username: Your PyPI username
- Password: Your PyPI password (or API token)

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

The workflow uses GitHub environments for approval gates:

1. Go to your GitHub repository settings
2. Click "Environments"
3. Create two environments:

### TestPyPI Environment
- Name: `testpypi`
- No protection rules needed (auto-deploy)

### PyPI Environment (with approval)
- Name: `pypi`
- Add protection rules:
  - ✅ Required reviewers: Add yourself or team members
  - This creates the approval gate before production deployment

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

If you prefer, do a manual upload first:

```bash
# Build the package
python -m build

# Upload to TestPyPI first (test)
python -m twine upload --repository testpypi dist/*

# If successful, upload to PyPI
python -m twine upload dist/*
```

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

## Current Package Status

The package has been built successfully:
- Source distribution: `dist/gitspaces-2.0.36.tar.gz`
- Wheel: `dist/gitspaces-2.0.36-py3-none-any.whl`

You can now upload these to reserve the name!
