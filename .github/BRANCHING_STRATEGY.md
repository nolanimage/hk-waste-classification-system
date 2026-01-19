# Branching Strategy for QA and Production

This document outlines the Git branching strategy for managing QA (testing) and production environments.

## Branch Structure

```
main (production)
  └── develop (QA/testing)
      └── feature/* (feature branches)
```

## Branches

### `main` Branch
- **Purpose**: Production-ready code
- **Protection**: Should be protected (require PR reviews)
- **Deployment**: Deploys to production environment
- **Merges**: Only from `develop` branch via Pull Requests

### `develop` Branch
- **Purpose**: QA/Testing environment
- **Protection**: Can be merged directly for testing
- **Deployment**: Deploys to QA/staging environment
- **Merges**: Feature branches merge here first

### `feature/*` Branches
- **Purpose**: New features or fixes
- **Naming**: `feature/description` (e.g., `feature/add-caching`)
- **Merges**: Into `develop` first, then to `main` after QA approval

## Workflow

### 1. Starting a New Feature

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add feature description"

# Push to GitHub
git push -u origin feature/your-feature-name
```

### 2. Testing in QA (develop branch)

```bash
# Merge feature to develop
git checkout develop
git pull origin develop
git merge feature/your-feature-name
git push origin develop

# Deploy develop branch to QA environment
```

### 3. Promoting to Production (main branch)

```bash
# After QA approval, merge develop to main
git checkout main
git pull origin main
git merge develop
git push origin main

# Create a release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Environment Configuration

### Production Environment Variables

Create `.env.production` (DO NOT commit to git):
```bash
OPENROUTER_API_KEY=your_production_key
VISION_MODEL=qwen/qwen3-vl-32b-instruct
# ... other production settings
```

### QA Environment Variables

Create `.env.qa` (DO NOT commit to git):
```bash
OPENROUTER_API_KEY=your_qa_test_key
VISION_MODEL=qwen/qwen3-vl-32b-instruct
# ... other QA settings
```

## GitHub Branch Protection Rules

### For `main` Branch:
1. Require pull request reviews before merging
2. Require status checks to pass
3. Require branches to be up to date
4. Do not allow force pushes
5. Do not allow deletions

### For `develop` Branch:
1. Require pull request reviews (optional, can be less strict)
2. Allow force pushes (for hotfixes, if needed)

## Release Process

1. **Development**: Work on `feature/*` branches
2. **QA Testing**: Merge to `develop`, test in QA environment
3. **Production Release**: After QA approval, merge `develop` → `main`
4. **Tagging**: Create version tags on `main` branch
5. **Hotfixes**: Create `hotfix/*` branches from `main` if needed

## Quick Reference

```bash
# Create feature branch
git checkout -b feature/new-feature develop

# Merge to QA
git checkout develop
git merge feature/new-feature
git push origin develop

# Release to production
git checkout main
git merge develop
git tag v1.0.0
git push origin main --tags
```

## Best Practices

1. **Never commit directly to `main`** - Always use PRs
2. **Test in `develop` first** - QA all changes before production
3. **Use descriptive branch names** - `feature/add-user-feedback`
4. **Keep branches up to date** - Regularly merge `develop` into feature branches
5. **Delete merged branches** - Clean up after merging
6. **Use semantic versioning** - v1.0.0, v1.1.0, v2.0.0
