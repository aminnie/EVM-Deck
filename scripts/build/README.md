# Build Scripts

This directory contains build scripts for packaging DevDeck for different platforms.

## Available Builds

### macOS (`build-macos.sh`)
Creates a self-contained macOS .app bundle and .dmg disk image.

**Requirements:**
- macOS 10.13+
- Python 3.12+
- Homebrew (for libusb and hidapi)
- py2app

**Usage:**
```bash
./scripts/build/build-macos.sh
```

**Output:**
- `dist/DevDeck.app` - Application bundle
- `dist/DevDeck.dmg` - Disk image for distribution

See [MACOS_PACKAGING.md](../../docs/MACOS_PACKAGING.md) for detailed documentation.

### Raspberry Pi (Coming Soon)
Raspberry Pi build scripts will be added in the future for creating installable packages.

## Build Structure

Each platform has its own:
- Build script (e.g., `build-macos.sh`)
- Setup configuration (e.g., `setup_macos.py`)
- Platform-specific documentation

## Running Builds

All build scripts should be run from the project root:
```bash
cd devdeck-main
./scripts/build/build-<platform>.sh
```

## Branch Strategy

Build-related changes are kept on separate branches:
- `build/macos-packaging` - macOS build support
- `build/raspberry-pi` - Raspberry Pi build support (future)

This allows:
- Main branch to remain stable
- Easy switching between build configurations
- Independent testing of build processes
- Clean merge when ready

