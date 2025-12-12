# macOS Packaging Guide

This guide explains how to package DevDeck as a self-contained macOS application bundle (.app) and create a .dmg disk image for distribution.

## Overview

The packaging process creates:
- A `.app` bundle containing the Python runtime, all dependencies, and system libraries
- A `.dmg` disk image for easy distribution

The packaged application is self-contained and does not require Python, Homebrew, or any other dependencies to be pre-installed on the target Mac.

## Prerequisites

### System Requirements
- macOS 10.13 (High Sierra) or later
- Python 3.12 or higher
- Xcode Command Line Tools
- Homebrew (for system libraries)

### Required Software

1. **Python 3.12+**
   ```bash
   python3 --version
   ```

2. **py2app** (will be installed automatically if missing)
   ```bash
   pip3 install py2app
   ```

3. **System Libraries** (install via Homebrew):
   ```bash
   brew install libusb
   brew install hidapi
   ```

4. **Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

## Building the Application

### Step 1: Prepare the Environment

1. Navigate to the project root:
   ```bash
   cd devdeck-main
   ```

2. Ensure all Python dependencies are installed:
   ```bash
   pip3 install -r requirements.txt
   ```

### Step 2: Run the Build Script

Execute the build script:
```bash
./scripts/build/build-macos.sh
```

The script will:
1. Check prerequisites (Python version, py2app, system libraries)
2. Build the `.app` bundle using py2app
3. Copy system libraries (libusb, hidapi) into the bundle
4. Fix library paths using `install_name_tool`
5. Create a `.dmg` disk image

### Step 3: Verify the Build

After the build completes, you should have:
- `dist/DevDeck.app` - The application bundle
- `dist/DevDeck.dmg` - The disk image for distribution

Test the application:
```bash
open dist/DevDeck.app
```

## Build Output

### Application Bundle Structure

```
DevDeck.app/
  Contents/
    MacOS/
      DevDeck (executable)
    Resources/
      lib/ (Python runtime)
      site-packages/ (Python dependencies)
      devdeck/ (application code)
      assets/ (images, icons)
      config/ (templates)
    Frameworks/
      libusb-1.0.dylib
      libhidapi.dylib
    Info.plist (app metadata)
```

### Disk Image Contents

The `.dmg` file contains:
- `DevDeck.app` - The application bundle
- `Applications` - Symlink to `/Applications` for easy installation

## Distribution

### Sharing the Application

1. **Share the .dmg file**: Upload `dist/DevDeck.dmg` to your distribution platform
2. **User Installation**:
   - Users download the `.dmg` file
   - Double-click to mount the disk image
   - Drag `DevDeck.app` to the `Applications` folder
   - Eject the disk image

### First Run on User's Mac

When users first run the application:
- macOS may show a security warning (since the app is not code-signed)
- Users need to:
  1. Right-click the app and select "Open"
  2. Click "Open" in the security dialog
  3. Or go to System Preferences > Security & Privacy and click "Open Anyway"

**Note**: For distribution outside the App Store, code signing and notarization are recommended but not implemented in this build (as per plan requirements).

## Troubleshooting

### Build Errors

#### "py2app not found"
```bash
pip3 install py2app
```

#### "libusb not found" or "hidapi not found"
```bash
brew install libusb
brew install hidapi
```

#### "Python 3.12+ required"
Ensure you're using Python 3.12 or higher. Check with:
```bash
python3 --version
```

If you have multiple Python versions, you may need to use `python3.12` explicitly.

### Runtime Errors

#### "Library not loaded" errors
The build script should handle library paths automatically. If you see library loading errors:
1. Verify the libraries are in `DevDeck.app/Contents/Frameworks/`
2. Check library paths with:
   ```bash
   otool -L DevDeck.app/Contents/MacOS/DevDeck
   ```

#### USB Device Access Issues
- The application requires USB access for Stream Deck and MIDI devices
- macOS may prompt for USB permissions on first run
- If devices aren't detected, check System Preferences > Security & Privacy > Privacy > USB

#### Path Resolution Issues
- The application uses `devdeck/path_utils.py` to handle paths in both development and bundled modes
- If you see path-related errors, verify the bundle structure matches the expected layout

### Testing the Bundle

Before distributing, test the bundle on a clean macOS system (or a VM):
1. Copy `DevDeck.app` to a test machine
2. Ensure no Python or Homebrew is installed
3. Run the application and verify:
   - GUI starts correctly
   - Stream Deck detection works
   - MIDI device detection works
   - Configuration files are created in `~/.devdeck/`
   - Assets (icons, images) load correctly

## Build Configuration

### Customizing the Build

Edit `setup_macos.py` to customize:
- Application name and version
- Bundle identifier
- Minimum macOS version
- Included/excluded packages
- Info.plist settings

### Build Script Options

The build script (`scripts/build/build-macos.sh`) can be modified to:
- Change the DMG volume name
- Add custom icons
- Include additional files
- Customize library bundling

## Technical Details

### Path Resolution

The application uses `devdeck/path_utils.py` to detect whether it's running:
- **Development mode**: From source code
- **Bundled mode**: From a .app bundle

Paths are resolved accordingly:
- **Project root**: Development uses source root, bundle uses `Contents/Resources/`
- **Config directory**: Development uses `config/`, bundle uses `~/.devdeck/` for user configs
- **Assets**: Development uses `devdeck/assets/`, bundle uses `Resources/devdeck/assets/`
- **Logs**: Development uses `logs/`, bundle uses `~/.devdeck/logs/`

### System Library Bundling

System libraries (libusb, hidapi) are:
1. Located via Homebrew paths (`/opt/homebrew/lib/` for Apple Silicon, `/usr/local/lib/` for Intel)
2. Copied to `Contents/Frameworks/` in the bundle
3. Library paths are fixed using `install_name_tool` to use `@executable_path/../Frameworks/`

### Python Runtime Bundling

py2app bundles:
- Python interpreter
- Standard library
- All installed packages (from `requirements.txt`)
- Application code

The bundle is self-contained and doesn't require system Python.

## Advanced Topics

### Code Signing (Optional)

To code sign the application (required for distribution outside App Store):
1. Obtain an Apple Developer certificate
2. Sign the bundle:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" DevDeck.app
   ```
3. Notarize with Apple:
   ```bash
   xcrun notarytool submit DevDeck.app --keychain-profile "notary-profile" --wait
   ```

### Creating a Custom Icon

1. Create an `.icns` file (use `iconutil` or online converters)
2. Update `setup_macos.py`:
   ```python
   'iconfile': 'path/to/icon.icns',
   ```

### Reducing Bundle Size

To reduce the bundle size:
1. Exclude unnecessary packages in `setup_macos.py`
2. Use `--optimize` flag in py2app (not recommended for debugging)
3. Strip debug symbols (advanced)

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review [USER_GUIDE.md](USER_GUIDE.md) for application usage
- Check [MAC_QUICK_START.md](MAC_QUICK_START.md) for macOS-specific setup

