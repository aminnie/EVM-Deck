# Raspberry Pi GUI Quick Start Guide

## Overview

This guide provides quick instructions for running the EVMDeck application with the GUI Control Panel on Raspberry Pi. The GUI is optimized for 480x272 pixel displays, making it perfect for small touchscreen displays.

## Prerequisites

### 1. Install tkinter

The GUI requires `tkinter`, which may not be installed by default:

```bash
sudo apt-get update
sudo apt-get install -y python3-tk
```

### 2. Verify tkinter Installation

Test that tkinter is available:

```bash
python3 -c "import tkinter; print('✓ tkinter is available')"
```

### 3. Display Requirements

The GUI requires a graphical display:

- **Direct Display**: Connect a monitor, TV, or touchscreen display directly to the Raspberry Pi
- **VNC**: Use VNC server for remote desktop access
- **X11 Forwarding**: If using SSH, enable X11 forwarding (not recommended for production)

**Note**: The GUI window is sized at 480x272 pixels, which matches common small Raspberry Pi touchscreen displays.

## Quick Start

### Step 1: Activate Virtual Environment

```bash
cd ~/devdeck
source venv/bin/activate
```

### Step 2: Run Application with GUI

```bash
# GUI starts automatically (default)
python3 -m devdeck.main
```

The GUI window will open automatically when the application starts.

### Step 3: Using the GUI

1. **Start the Application**: Click the "Start" button
   - Stream Deck will initialize
   - Status changes to "Status: Running" (green)
   - MIDI monitoring starts automatically

2. **Monitor Key Presses**: Press keys on your Stream Deck
   - Key presses appear in the "Keys Monitor" section
   - Format: `[HH:MM:SS] Pressed KeyName [MIDI Hex]`
   - Example: `[14:23:45] Pressed Fill [F0 26 79 03 15 7F F7]`

3. **View USB Devices**: Check the "USB Devices" section
   - Shows detected Elgato Stream Deck
   - Shows detected MIDI output device
   - Click "Refresh Devices" to rescan

4. **Exit**: Click "Exit" button or close the window

## Running Without GUI

If you prefer to run without the GUI (e.g., for headless operation or as a service):

```bash
python3 -m devdeck.main --no-gui
```

## GUI Features

### Application Control
- **Start Button**: Start the EVMDeck application
- **Exit Button**: Gracefully stop and exit
- **Status Indicator**: Shows "Running" (green) or "Stopped" (red)

### USB Devices
- **USB Input Device**: Elgato Stream Deck with vendor name
- **USB Output Device**: MIDI output device with vendor name
- **Refresh Devices Button**: Rescan USB devices

### Keys Monitor
- Real-time display of Stream Deck key presses
- Timestamp for each key press
- Key name (e.g., "Fill", "Break", "Start/Stop")
- MIDI message in hex format (SysEx or CC)
- Automatically scrolls to show recent presses

## Troubleshooting

### GUI Window Doesn't Appear

1. **Check tkinter**:
   ```bash
   python3 -c "import tkinter; print('tkinter OK')"
   ```
   If this fails: `sudo apt-get install python3-tk`

2. **Verify display**:
   ```bash
   echo $DISPLAY
   ```
   Should show `:0` or `:0.0`. If empty, you may be in a headless environment.

3. **Check if running via SSH without X11**:
   - Use VNC or connect directly to a monitor
   - Or run with `--no-gui` flag

### "No module named 'tkinter'" Error

**Solution**: Install tkinter:
```bash
sudo apt-get install -y python3-tk
```

### USB Devices Show "None"

1. Click "Refresh Devices" button
2. Verify devices are connected:
   ```bash
   lsusb | grep -i elgato  # Stream Deck
   lsusb | grep -i midi   # MIDI device
   ```

### Key Presses Not Showing

1. Ensure application is started (click "Start" button)
2. Check that MIDI monitoring started (should see ready message)
3. Verify Stream Deck is working
4. Check terminal for error messages

## GUI and Service Mode

**Important**: When running as a systemd service, use the `--no-gui` flag:

```bash
# In systemd service file
ExecStart=/home/admin/devdeck/venv/bin/python3 -m devdeck.main --no-gui
```

Services typically don't have display access, so the GUI won't work in service mode.

## Best Practices

1. **For Development/Testing**: Use GUI mode for easy monitoring
2. **For Production/Service**: Use `--no-gui` mode when running as a service
3. **Display Setup**: Use a small touchscreen (480x272) for best experience
4. **Remote Access**: Use VNC if you need GUI access remotely

## Example GUI Output

When you press keys on your Stream Deck, you'll see messages like:

```
[14:23:45] Pressed Fill [F0 26 79 03 15 7F F7]
[14:23:46] Pressed Break [F0 26 79 03 16 7F F7]
[14:23:47] Pressed Voice1 [BF 72 40]
[14:23:48] Pressed Volume Up [BF 6C 41]
[14:23:49] Pressed Mute [BF 6C 00]
```

- **SysEx Messages**: Full hex string with F0 (start) and F7 (end)
- **CC Messages**: Format `Bn CC VV` (status byte, control, value)

## Next Steps

- See [RASPBERRY_PI_DEPLOYMENT.md](RASPBERRY_PI_DEPLOYMENT.md) for full deployment guide
- See [USER_GUIDE.md](USER_GUIDE.md) for application usage
- Configure your Stream Deck: Edit `config/settings.yml`
- Set up MIDI mappings: Edit `config/key_mappings.json`

