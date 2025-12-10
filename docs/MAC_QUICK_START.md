# Mac Quick Start Guide - Updated Application with GUI

## What's New

The application now includes a **GUI Control Panel** that provides:
- Start/Stop/Restart buttons for application control
- Real-time MIDI key press monitoring
- Display of connected MIDI input and output devices
- Status indicators

## Prerequisites Check

Before running, ensure you have:

1. **System Dependencies** (install via Homebrew if not already installed):
   ```bash
   brew install libusb
   brew install hidapi
   brew install usbutils
   ```

2. **Python 3.12+** installed:
   ```bash
   python3 --version
   ```

3. **Xcode Command Line Tools** (if not already installed):
   ```bash
   xcode-select --install
   ```

## Running the Updated Application

### Step 1: Navigate to Project Directory
```bash
cd devdeck-main  # or your project path
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

If you don't have a virtual environment yet:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python3 -m devdeck.main
```

**The GUI window will open automatically!**

### Step 4: Using the GUI

1. **Start the Application**: Click the "Start" button to begin the DevDeck application
2. **Monitor MIDI**: Click "Start MIDI Monitor" to see MIDI key presses in real-time
3. **View Devices**: The GUI shows your connected MIDI input and output devices
4. **Control Application**: Use Start/Stop/Restart buttons as needed

### Running Without GUI (Optional)

If you prefer the command-line interface:
```bash
python3 -m devdeck.main --no-gui
```

## GUI Requirements

- **tkinter**: Included with Python on macOS (no installation needed)
- **Display**: Requires a graphical display (local Mac or via X11/VNC if remote)

## Troubleshooting

### GUI Window Doesn't Appear

1. **Check tkinter availability**:
   ```bash
   python3 -c "import tkinter; print('tkinter OK')"
   ```

2. **If tkinter is missing** (rare on macOS):
   ```bash
   brew install python-tk
   ```

3. **Verify you're not in a headless environment**:
   - GUI requires a display
   - If SSH'd in, use X11 forwarding or VNC

### Application Won't Start

1. **Check USB devices**:
   ```bash
   lsusb | grep -i elgato  # Stream Deck
   lsusb | grep -i midi    # MIDI device
   ```

2. **Verify dependencies**:
   ```bash
   pip list | grep -E "(mido|streamdeck|devdeck-core)"
   ```

3. **Check logs**: Look for error messages in the terminal

### MIDI Devices Not Showing

1. **Refresh devices**: Click the "Refresh Devices" button in the GUI
2. **Check MIDI ports**:
   ```bash
   python3 -c "import mido; print(mido.get_input_names()); print(mido.get_output_names())"
   ```

## Quick Reference

| Command | Description |
|--------|-------------|
| `python3 -m devdeck.main` | Run with GUI (default) |
| `python3 -m devdeck.main --no-gui` | Run without GUI |
| `source venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install/update dependencies |

## Next Steps

- Configure your Stream Deck: Edit `config/settings.yml`
- Set up MIDI mappings: Edit `config/key_mappings.json`
- See [USER_GUIDE.md](USER_GUIDE.md) for detailed configuration
- See [mac_midi_install.md](mac_midi_install.md) for full Mac installation guide

