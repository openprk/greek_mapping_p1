# Branch Guide

## Branches

- **main**: Production-ready code
- **dev**: Development branch for testing changes before merging to main

## Working with Branches

### Switch to dev branch
```bash
git checkout dev
```

### Switch back to main
```bash
git checkout main
```

### Make changes on dev branch
```bash
# Switch to dev
git checkout dev

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Your commit message"

# Push to dev branch
git push origin dev
```

### Merge dev into main (when ready)
```bash
# Switch to main
git checkout main

# Merge dev into main
git merge dev

# Push to GitHub
git push origin main
```

### Create a new feature branch from dev
```bash
# Make sure you're on dev
git checkout dev

# Create and switch to new feature branch
git checkout -b feature/your-feature-name

# Make changes, commit, push
git add .
git commit -m "Add new feature"
git push -u origin feature/your-feature-name
```

## Current Branch Status

Check which branch you're on:
```bash
git branch
```

The current branch will have an asterisk (*) next to it.

## Best Practices

1. **Always work on dev** for new features/changes
2. **Test thoroughly** on dev before merging to main
3. **Keep main stable** - only merge when code is ready
4. **Use feature branches** for larger changes (branch from dev, merge back to dev)

