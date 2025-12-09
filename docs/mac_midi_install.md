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

----



