# Build Workflow Guide

This guide explains how to work with the build branches and create platform-specific packages.

## Branch Overview

- **`main`** - Stable production code (no build-specific changes)
- **`build/macos-packaging`** - macOS build support with py2app
- **`build/raspberry-pi`** - Raspberry Pi build support (future)

## Switching Between Branches

### To Work on macOS Builds

```bash
# Switch to macOS build branch
git checkout build/macos-packaging

# Pull latest changes
git pull origin build/macos-packaging

# Run the build (on macOS)
./scripts/build/build-macos.sh
```

### To Return to Main Branch

```bash
# Switch back to main
git checkout main

# Your working directory will be clean (no build changes)
```

## Building on macOS

### Prerequisites Check

Before building, ensure you have:
1. **Python 3.12+**: `python3 --version`
2. **Homebrew libraries**: `brew list libusb hidapi`
3. **py2app**: `pip3 install py2app`

### Build Process

1. **Switch to build branch**:
   ```bash
   git checkout build/macos-packaging
   ```

2. **Install dependencies** (if not already done):
   ```bash
   pip3 install -r requirements.txt
   pip3 install py2app
   ```

3. **Make script executable** (first time only, if needed):
   ```bash
   chmod +x scripts/build/build-macos.sh
   ```

4. **Run the build script**:
   ```bash
   ./scripts/build/build-macos.sh
   ```
   
   **Or run with bash** (no chmod needed):
   ```bash
   bash scripts/build/build-macos.sh
   ```

4. **Output**:
   - `dist/DevDeck.app` - Application bundle
   - `dist/DevDeck.dmg` - Disk image for distribution

5. **Test the bundle**:
   ```bash
   open dist/DevDeck.app
   ```

## Making Changes

### Updating Build Configuration

If you need to modify the build:
1. Make changes on the `build/macos-packaging` branch
2. Test the build
3. Commit changes:
   ```bash
   git add <modified-files>
   git commit -m "Update macOS build configuration"
   git push origin build/macos-packaging
   ```

### Updating Application Code

If you need to update application code that affects builds:
1. Make changes on `main` branch first
2. Merge or cherry-pick to build branch:
   ```bash
   git checkout build/macos-packaging
   git merge main
   # Or cherry-pick specific commits
   git cherry-pick <commit-hash>
   ```

## Future: Raspberry Pi Builds

When ready to add Raspberry Pi builds:

1. **Create new branch from main**:
   ```bash
   git checkout main
   git checkout -b build/raspberry-pi
   ```

2. **Create Raspberry Pi build files**:
   - `setup_raspberry_pi.py` (or similar)
   - `scripts/build/build-raspberry-pi.sh`
   - `docs/RASPBERRY_PI_PACKAGING.md`

3. **Follow similar structure to macOS builds**

## Merging Build Changes to Main

When build support is stable and ready for production:

1. **Test thoroughly on the build branch**
2. **Merge to main** (when ready):
   ```bash
   git checkout main
   git merge build/macos-packaging
   ```

   Or create a pull request for review.

## Troubleshooting

### Build Script Fails

- Check prerequisites are installed
- Verify you're on the correct branch
- Check build script logs for specific errors
- See [MACOS_PACKAGING.md](MACOS_PACKAGING.md) for detailed troubleshooting

### Path Issues After Branch Switch

- The `path_utils.py` module handles both development and bundle modes
- If you see path errors, ensure you're using the build branch when building

### Conflicts When Merging

- Build-specific files (like `setup_macos.py`) should only exist on build branches
- Application code changes should be made on `main` first, then merged to build branches

## Quick Reference

| Task | Command |
|------|---------|
| Switch to macOS build | `git checkout build/macos-packaging` |
| Switch to main | `git checkout main` |
| Run macOS build | `./scripts/build/build-macos.sh` |
| View build branch | `git branch -a` |
| Check current branch | `git branch` |

