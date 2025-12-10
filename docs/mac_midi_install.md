# macOS Portability Guide - Mac M4 Mini

## Overview

Yes, the devdeck Python libraries are portable to a Mac M4 Mini. Since you don't use audio controls, the main blockers are removed.

## Core Libraries - macOS Compatible

1. **`devdeck-core==1.0.7`** - Cross-platform Python library; works on macOS
2. **`streamdeck` (python-elgato-streamdeck)** - Supports macOS (uses libusb/HIDAPI, which has macOS support)
3. **`mido` + `python-rtmidi`** - Cross-platform MIDI; macOS uses CoreMIDI
4. **Other dependencies** (Pillow, PyYAML, Cerberus, etc.) - All support macOS ARM64

## What to Verify on macOS

### 1. System Dependencies

You'll need:
- `libusb` (for Stream Deck USB communication)
- Python 3.12+ (ARM64 native)

### 2. Installation Steps

```bash
# Install system dependencies (using Homebrew)
brew install libusb

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. MIDI Support

The code already handles macOS - virtual MIDI ports work on macOS (as seen in `midi_manager.py` line 180). The MIDI implementation uses `mido` with `python-rtmidi` backend, which supports macOS CoreMIDI.

## Summary

The application should work on a Mac M4 Mini. The README explicitly lists macOS as a supported platform, and the core libraries are all cross-platform. Since you don't use audio controls, the `pulsectl` dependency isn't a concern.

The main thing to ensure is that `libusb` is installed on macOS (via Homebrew) for Stream Deck USB communication. Everything else should work out of the box.

## Notes

- The `pulsectl` dependency in `requirements.txt` is only used for audio controls (VolumeLevelControl, VolumeMuteControl, MicMuteControl), which you don't use
- The MIDI manager already has platform detection for macOS support
- All Python dependencies are cross-platform and support macOS ARM64



---------------------------

## Extracted from the Mac Mini terminal logs. This reflects what we had to do really get the app up and runnung

brew install python
pip3 install virtualenv
mkdir evmdeck
rm -r evmdeck
mkdir evmdeck
virtualenv -p python3 evmdeck
source evmdeck/bin/activate
cd evmdeck
source bin/activate
git clone git@github.com:aminnie/EVM-Deck.git evmdeck
cd evmdeck
git init
python3 -m pip install -r requirements.txt
xcode-select --install
python3 -m pip install wheel
python3 -m pip install -r requirements.txt
python3 -m pip install --upgrade pip
python3 -m pip install wheel
python3 -m pip install -r requirements.txt
python3 -m pip install pillow
python3 -m pip install -r requirements.txt
python3 -m pip install pillow
python3 -m pip install wheel
nano  requirements.txt
python3 -m pip install -r requirements.txt
ls
python3 -m pip install --force-reinstall streamdeck
pip list | grep streamdeck
python3 -m devdeck.main
lsusb
brew install libusb
brew install usbutils
lsusb
python3 -m devdeck.main
cd evmdeck
source bin/activate
python3 -m devdeck.main
lsusb

Note:
1. On the Mac we were missing: libhidapi.dylib. 
    Fixed by installing: brew install hidapi.

    This is in addition to: 
        brew install libusb
        brew install usbutils

2. We needed to manually change the file:

If you need to keep a newer Pillow or the reinstall doesn't work, apply the same fix you used on Raspberry PI. 
The file location on Mac will be:
venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py
Find the file:
find venv -name "text_renderer.py" -path "*/devdeck_core/*"
Then edit it and replace line 51 (or wherever textsize is used):
# OLD (line 51):
label_w, label_h = draw.textsize('%s' % self.text, font=font)
# NEW:
# textsize() was deprecated and removed in Pillow 10.0.0, use textbbox() instead
bbox = draw.textbbox((0, 0), '%s' % self.text, font=font)
label_w = bbox[2] - bbox[0]  # right - left
label_h = bbox[3] - bbox[1]  # bottom - top

If you need to keep a newer Pillow or the reinstall doesn't work, apply the same fix you used on Raspberry PI. The file location on Mac will be:

venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py
Find the file:
find venv -name "text_renderer.py" -path "*/devdeck_core/*"
Then edit it and replace line 51 (or wherever textsize is used):
# OLD (line 51):
label_w, label_h = draw.textsize('%s' % self.text, font=font)
# NEW:
# textsize() was deprecated and removed in Pillow 10.0.0, use textbbox() instead
bbox = draw.textbbox((0, 0), '%s' % self.text, font=font)
label_w = bbox[2] - bbox[0]  # right - left
label_h = bbox[3] - bbox[1]  # bottom - top

If you need to find /Library/Frameworks because it's a standard system folder, but sometimes hidden or moved; you can access it via Finder > Go > Go to Folder (Shift+Cmd+G) and type /Library/Frameworks, or use the specific path /System/Library/Frameworks

----

## Running the Updated Application with GUI

### GUI Requirements

The new GUI control panel uses **tkinter**, which is included with Python on macOS. No additional installation is required for the GUI itself.

### Running the Application

1. **Navigate to the project directory**:
   ```bash
   cd devdeck-main  # or wherever your project is located
   ```

2. **Activate your virtual environment** (if using one):
   ```bash
   source venv/bin/activate
   ```

3. **Run the application** (GUI starts by default):
   ```bash
   python3 -m devdeck.main
   ```

   The GUI control panel window will open automatically.

4. **To run without GUI** (if needed):
   ```bash
   python3 -m devdeck.main --no-gui
   ```

### GUI Features on Mac

The GUI provides:
- **Application Control**: Start, Stop, and Restart buttons
- **MIDI Device Display**: Shows connected MIDI input and output devices
- **MIDI Key Monitor**: Real-time display of MIDI Note ON/OFF messages
- **Status Indicators**: Visual feedback for application and MIDI states

### Troubleshooting GUI on Mac

**Issue**: GUI window doesn't appear or crashes immediately

**Solutions**:
1. **Check Python GUI support**:
   ```bash
   python3 -c "import tkinter; print('tkinter available')"
   ```
   If this fails, you may need to install Python with GUI support (most Python installations include it).

2. **Check if running in a headless environment**:
   - Make sure you're not SSH'd into the Mac without X11 forwarding
   - The GUI requires a display (local or via X11/VNC)

3. **Verify Python version**:
   ```bash
   python3 --version  # Should be 3.12 or higher
   ```

**Issue**: "No module named 'tkinter'" error

**Solution**: On some macOS installations, tkinter may need to be installed separately:
```bash
# For Homebrew Python
brew install python-tk

# Or reinstall Python with GUI support
brew reinstall python@3.12
```

**Note**: Most standard Python installations on macOS include tkinter by default.

### First Run Checklist

Before running the updated application:

- [ ] System dependencies installed (`libusb`, `hidapi`)
- [ ] Virtual environment activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Stream Deck connected via USB
- [ ] MIDI device connected (if using MIDI features)
- [ ] Official Stream Deck application is closed

### Quick Start Command

```bash
# One-liner to activate venv and run (if already set up)
cd devdeck-main && source venv/bin/activate && python3 -m devdeck.main
```

----



