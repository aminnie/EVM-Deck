# macOS Packaging Troubleshooting

This document addresses common issues when building and running macOS .app bundles.

## Persistent Code Signature Errors

### Symptom
App crashes immediately with:
- "Code Signature Invalid"
- "main_executable_path_missing"
- EXC_BAD_ACCESS (SIGKILL)

### Possible Causes

1. **Python 3.14.0 Compatibility**
   - py2app may not fully support Python 3.14.0 yet
   - **Solution**: Try Python 3.12 or 3.13

2. **macOS 26.1 Compatibility**
   - Very new/beta macOS versions may have stricter security
   - **Solution**: Test on stable macOS version (14.x or 15.x)

3. **py2app Build Issues**
   - Executable may not be created correctly
   - **Solution**: Use diagnostic script to verify

### Diagnostic Steps

1. **Run diagnostic script**:
   ```bash
   chmod +x scripts/build/diagnose-app.sh
   ./scripts/build/diagnose-app.sh dist/DevDeck.app
   ```

2. **Check executable directly**:
   ```bash
   file dist/DevDeck.app/Contents/MacOS/DevDeck
   head -20 dist/DevDeck.app/Contents/MacOS/DevDeck
   ```

3. **Run from Terminal** (shows Python errors):
   ```bash
   ./dist/DevDeck.app/Contents/MacOS/DevDeck
   ```

4. **Check code signature**:
   ```bash
   codesign -dv dist/DevDeck.app
   codesign --verify --verbose dist/DevDeck.app
   ```

### Workarounds

#### Option 1: Use Python 3.12 or 3.13

```bash
# Install Python 3.12 via Homebrew
brew install python@3.12

# Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install py2app

# Rebuild
./scripts/build/build-macos.sh
```

#### Option 2: Try PyInstaller (Alternative)

If py2app continues to have issues, PyInstaller is an alternative:

```bash
pip install pyinstaller

# Create spec file
pyinstaller --name=DevDeck \
    --windowed \
    --onedir \
    --add-data "devdeck/assets:devdeck/assets" \
    --add-data "config:config" \
    devdeck/main.py

# This creates dist/DevDeck/ directory
# You can then create a .app bundle manually or use create-dmg
```

#### Option 3: Run from Source (Development)

For development/testing, run directly from source:

```bash
source venv/bin/activate
python -m devdeck.main
```

This avoids packaging issues entirely.

## Other Common Issues

### "Library not loaded" Errors

If you see library loading errors:

1. **Verify libraries are bundled**:
   ```bash
   ls -la dist/DevDeck.app/Contents/Frameworks/
   ```

2. **Check library paths**:
   ```bash
   otool -L dist/DevDeck.app/Contents/MacOS/DevDeck
   ```

3. **Rebuild with updated script** (should fix paths automatically)

### GUI Doesn't Appear

If the app runs but GUI doesn't show:

1. Check if running in headless mode
2. Verify tkinter is included in bundle
3. Check Console.app for error messages

### USB Device Not Detected

1. Grant USB permissions in System Preferences > Security & Privacy
2. Check System Information > USB to verify device is connected
3. Run diagnostic: `lsusb | grep -i elgato`

## Getting Help

When reporting issues, include:

1. **macOS version**: `sw_vers`
2. **Python version**: `python3 --version`
3. **Diagnostic output**: `./scripts/build/diagnose-app.sh dist/DevDeck.app`
4. **Terminal output**: Run executable from Terminal and capture output
5. **Build logs**: Full output from `./scripts/build/build-macos.sh`

## Known Limitations

- Code signing not implemented (for personal/internal use)
- Notarization not implemented
- May require right-click "Open" on first run
- Python 3.14.0 compatibility untested
- macOS 26.1 compatibility untested

