# Raspberry Pi 5 Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Operating System Setup](#operating-system-setup)
4. [System Dependencies](#system-dependencies)
5. [Python Environment Setup](#python-environment-setup)
6. [Application Installation](#application-installation)
7. [USB Permissions Configuration](#usb-permissions-configuration)
8. [MIDI Setup](#midi-setup)
9. [Application Configuration](#application-configuration)
10. [GUI Control Panel](#gui-control-panel)
11. [Samba Configuration (Windows Network Access)](#samba-configuration-windows-network-access)
12. [Running as a Service](#running-as-a-service)
13. [Auto-Start Configuration](#auto-start-configuration)
14. [Testing and Verification](#testing-and-verification)
15. [Troubleshooting](#troubleshooting)
16. [Maintenance](#maintenance)
17. [Development on Raspberry Pi 5](#development-on-raspberry-pi-5)

---

## Overview

This guide provides step-by-step instructions for deploying the Ketron EVM Stream Deck Controller application on a Raspberry Pi 5. The Raspberry Pi 5 is an excellent platform for this application due to its low power consumption, small form factor, and excellent Linux MIDI support.

### Why Raspberry Pi 5?

- **Low Power Consumption**: Can run 24/7 without significant power costs
- **Small Form Factor**: Easy to mount near your Ketron device
- **Native Linux MIDI Support**: ALSA MIDI works out of the box
- **Reliable**: Stable Linux environment for continuous operation
- **Cost-Effective**: Affordable hardware for dedicated control

---

## Hardware Requirements

### Required Hardware

1. **Raspberry Pi 5**
   - 4GB or 8GB RAM model (4GB is sufficient)
   - Official Raspberry Pi 5 power supply (27W USB-C)
   - MicroSD card (32GB or larger, Class 10 or better, recommended: 64GB)

2. **Elgato Stream Deck**
   - Any model (15-key, 32-key, etc.)
   - USB-A to USB-C cable (or appropriate adapter)

3. **Ketron Device Connection**
   - USB MIDI connection (direct USB)
   - OR MIDI interface (USB MIDI interface)
   - OR USB-to-MIDI cable

4. **Additional Items**
   - USB hub (if connecting multiple USB devices)
   - Case for Raspberry Pi (optional but recommended)
   - Heat sink or cooling fan (recommended for 24/7 operation)
   - Ethernet cable or Wi-Fi connection for initial setup

### Recommended Setup

- **Power**: Use official Raspberry Pi 5 power supply for stable operation
- **Cooling**: Add a heat sink or small fan for continuous operation
- **Storage**: Use a high-quality MicroSD card (SanDisk Extreme or similar)
- **USB Hub**: Powered USB hub if connecting multiple devices

---

## Operating System Setup

### Step 1: Download Raspberry Pi OS

1. Download **Raspberry Pi OS** (64-bit recommended):
   - Visit: https://www.raspberrypi.com/software/
   - Download Raspberry Pi Imager
   - Or download the OS image directly

2. **Recommended Version**: Raspberry Pi OS (64-bit) with desktop
   - Full desktop version is easier for initial setup
   - Can switch to Lite version later if desired

### Step 2: Flash OS to MicroSD Card

1. **Using Raspberry Pi Imager**:
   ```bash
   # Install Raspberry Pi Imager on your computer
   # Insert MicroSD card
   # Open Raspberry Pi Imager
   # Select OS: Raspberry Pi OS (64-bit)
   # Select storage: Your MicroSD card
   # Click Write
   ```

2. **Advanced Options** (Recommended):
   - Enable SSH
   - Set username and password
   - Configure Wi-Fi (if using wireless)
   - Set locale settings

### Step 3: First Boot

1. Insert MicroSD card into Raspberry Pi 5
2. Connect power supply
3. Connect to network (Ethernet or Wi-Fi)
4. Boot the system

### Step 4: Initial System Update

```bash
# Update package lists
sudo apt update

# Upgrade system packages
sudo apt upgrade -y

# Reboot if kernel was updated
sudo reboot
```

---

## System Dependencies

### Install Required System Packages

The application requires several system libraries for MIDI, USB, and Python development:

```bash
# Update package lists
sudo apt update

# Install essential build tools
sudo apt install -y build-essential python3-dev python3-pip python3-venv

# Install MIDI libraries (ALSA)
sudo apt install -y libasound2-dev libjack-dev libjack0

# Install USB libraries (for Stream Deck)
sudo apt install -y libusb-1.0-0-dev libhidapi-libusb0 libhidapi-dev

# Install additional dependencies
sudo apt install -y git curl wget

# Install ALSA utilities (for MIDI testing)
sudo apt install -y alsa-utils

# Install fonts (for text rendering on Stream Deck buttons)
sudo apt install -y fonts-dejavu fonts-liberation

# Install tkinter (for GUI support)
sudo apt install -y python3-tk

# Install Pillow build dependencies (required for building from source)
sudo apt install -y libjpeg-dev zlib1g-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev libimagequant-dev libraqm-dev

# Clean up
sudo apt autoremove -y
sudo apt autoclean
```

### Verify ALSA MIDI Support

```bash
# Check ALSA MIDI devices
aconnect -l

# List MIDI ports
amidi -l

# If no output, ALSA MIDI is working but no devices connected
```

---

## Python Environment Setup

### Step 1: Create Application Directory

```bash
# Create directory for application
mkdir -p ~/devdeck
cd ~/devdeck
```

### Step 2: Clone or Copy Application

**Option A: If using Git**:
```bash
git clone <repository-url> .
```

**Option B: If copying files**:
```bash
# Copy application files to ~/devdeck
# Ensure all files are present
```

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 4: Install Python Dependencies

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Expected Dependencies

You should see these packages installed:
- `streamdeck` - Elgato Stream Deck library (imported as `StreamDeck`)
- `mido` - MIDI library
- `python-rtmidi` - MIDI backend
- `devdeck-core` - Core Stream Deck library
- `pillow` - Image processing
- `pyyaml` - YAML configuration
- And others from requirements.txt

### Step 5: Verify StreamDeck Installation

After installing dependencies, verify that the StreamDeck library is properly installed:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Test StreamDeck import (correct syntax)
python3 -c "from StreamDeck.DeviceManager import DeviceManager; print('✓ StreamDeck library OK')"

# Test device enumeration (if Stream Deck is connected)
python3 -c "from StreamDeck.DeviceManager import DeviceManager; dm = DeviceManager(); decks = dm.enumerate(); print(f'Found {len(decks)} Stream Deck(s)')"
```

**Note**: The package name is `streamdeck` (lowercase) but Python imports it as `StreamDeck` (capitalized). If you get `ModuleNotFoundError`, ensure:
- Virtual environment is activated
- Dependencies are installed: `pip install -r requirements.txt`
- System USB libraries are installed: `sudo apt install -y libusb-1.0-0-dev`

---

## Application Installation

### Transferring Application Files to Raspberry Pi

After installing the OS, you need to transfer your application files from your development machine to the Raspberry Pi. Choose the method that works best for your setup:

#### Method 1: Using Git (Recommended)

If your application is in a Git repository, this is the easiest method:

**On Raspberry Pi:**
```bash
# Install Git if not already installed
sudo apt install -y git

# Navigate to home directory
cd ~

# Clone your repository
git clone <your-repository-url> devdeck

# Or if using SSH:
git clone git@github.com:username/repository.git devdeck

# Navigate to application directory
cd devdeck
```

**For updates later:**
```bash
cd ~/devdeck
git pull origin main  # or your branch name
```

#### Method 2: Using SCP (Secure Copy)

Transfer files directly from your Windows machine using SCP:

**On Windows (PowerShell or Command Prompt):**
```powershell
# Navigate to your application directory
cd C:\Users\a_min\devdeck-main

# Transfer entire directory (replace IP address)
scp -r * pi@192.168.1.100:~/devdeck/

# Or transfer specific files/folders
scp -r devdeck pi@192.168.1.100:~/devdeck/devdeck
scp -r config pi@192.168.1.100:~/devdeck/config
scp requirements.txt pi@192.168.1.100:~/devdeck/
```

**Note**: Replace `192.168.1.100` with your Raspberry Pi's IP address. Find it with:
```bash
# On Raspberry Pi
hostname -I
```

**First time connecting?** You'll be asked to accept the host key - type `yes`.

#### Method 3: Using USB Drive

**Step 1: Copy files to USB drive on Windows**
- Insert USB drive
- Copy entire `devdeck-main` folder to USB drive

**Step 2: Transfer to Raspberry Pi**
```bash
# Insert USB drive into Raspberry Pi
# Mount USB drive (usually auto-mounted)
lsblk  # List block devices to find USB drive

# If not auto-mounted, mount manually:
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb  # Adjust device name as needed

# Copy files
mkdir -p ~/devdeck
cp -r /mnt/usb/devdeck-main/* ~/devdeck/

# Unmount USB drive
sudo umount /mnt/usb
```

#### Method 4: Using Shared Network Folder (Samba)

Set up Samba to share the `~/devdeck` directory directly on your network. This allows you to access and edit files from Windows without copying them.

**For detailed Samba configuration instructions, see the [Samba Configuration section](#samba-configuration-windows-network-access).**

**Quick Setup Summary:**

1. **On Raspberry Pi:**
   ```bash
   # Install Samba
   sudo apt install -y samba samba-common-bin
   
   # Configure Samba (see detailed section for full instructions)
   sudo nano /etc/samba/smb.conf
   # Add devdeck share configuration
   
   # Set Samba password
   sudo smbpasswd -a pi
   
   # Restart Samba
   sudo systemctl restart smbd
   ```

2. **On Windows:**
   - Open File Explorer
   - Navigate to: `\\raspberry-pi-ip\devdeck` (replace with Pi's IP)
   - Enter credentials when prompted
   - You can now directly edit files in `~/devdeck` from Windows

**Note**: The detailed Samba configuration section provides secure setup options, troubleshooting tips, and performance optimizations.

#### Method 5: Using WinSCP (Windows GUI Tool)

1. **Download WinSCP**: https://winscp.net/
2. **Connect to Raspberry Pi**:
   - Host: Raspberry Pi IP address
   - Username: `pi` (or your username)
   - Password: Your Pi password
   - Protocol: SFTP
3. **Transfer files**:
   - Drag and drop files from Windows to Raspberry Pi
   - Navigate to `~/devdeck` on Raspberry Pi side
   - Copy all application files

#### Method 6: Using rsync (Advanced)

For efficient file synchronization:

**On Windows (using WSL or Git Bash):**
```bash
# Sync files (excludes venv and other unnecessary files)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
  /c/Users/a_min/devdeck-main/ pi@192.168.1.100:~/devdeck/
```

**On Raspberry Pi (if rsync server is set up):**
```bash
# Pull from remote location
rsync -avz user@remote:/path/to/devdeck-main/ ~/devdeck/
```

### Step 1: Verify Application Structure

After transferring files, verify everything is in place:

```bash
# Navigate to application directory
cd ~/devdeck

# List files
ls -la

# Should see:
# - devdeck/ (main package directory)
# - config/ (configuration files)
# - requirements.txt
# - README.md
# - setup.sh
# - run-devdeck.sh
# - etc.

# Verify key directories exist
ls -la devdeck/
ls -la config/

# Check configuration files
ls -la config/settings.yml
ls -la config/key_mappings.json
```

### Step 2: Set Proper Permissions

```bash
# Ensure you own all files
sudo chown -R $USER:$USER ~/devdeck

# Make scripts executable
chmod +x ~/devdeck/setup.sh
chmod +x ~/devdeck/scripts/run/run-devdeck.sh
```

### Step 3: Test Application Import

```bash
# Note: Virtual environment not created yet - that's next step
# But we can verify Python can find the module structure
cd ~/devdeck
python3 -c "import sys; sys.path.insert(0, '.'); from devdeck.midi import MidiManager; print('MIDI Manager OK')"
python3 -c "import sys; sys.path.insert(0, '.'); from devdeck.ketron import KetronMidi; print('Ketron MIDI OK')"
```

### Step 4: Verify Configuration Files

```bash
# Check JSON syntax
python3 -m json.tool config/key_mappings.json > /dev/null && echo "JSON valid" || echo "JSON invalid"

# Check YAML syntax (if pyyaml is installed)
python3 -c "import yaml; yaml.safe_load(open('config/settings.yml'))" && echo "YAML valid" || echo "YAML invalid"
```

---

## USB Permissions Configuration

### Stream Deck USB Access

The Stream Deck requires USB access. On Raspberry Pi, you may need to configure udev rules:

### Step 1: Find Stream Deck USB ID

```bash
# Connect Stream Deck
lsusb

# Look for Elgato or Stream Deck device
# Note the vendor and product IDs (e.g., 0fd9:0060)
```

### Step 2: Create udev Rule

```bash
# Create udev rule file
sudo nano /etc/udev/rules.d/50-streamdeck.rules
```

Add the following (adjust vendor/product IDs if different):
```
# Elgato Stream Deck
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0060", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006d", MODE="0666", GROUP="plugdev"
```

### Step 3: Add User to plugdev Group

```bash
# Check if plugdev group exists (it should on Raspberry Pi OS)
getent group plugdev

# If group doesn't exist, create it
sudo groupadd plugdev

# Add your user to plugdev group (for USB access)
sudo usermod -a -G plugdev $USER

# Add your user to audio group (for ALSA MIDI access)
sudo usermod -a -G audio $USER

# Verify you're in the groups
groups $USER
# Should show 'plugdev' and 'audio' in the list

# Apply changes - IMPORTANT: You must log out and log back in for this to take effect
# For the current session only, you can use:
newgrp plugdev
newgrp audio

# But for permanent effect, log out and log back in
```

### Step 4: Reload udev Rules

```bash
# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# IMPORTANT: Unplug and replug Stream Deck USB cable
# This is required for the new udev rules to take effect
```

**Note**: After modifying udev rules or changing group membership, you must:
1. Reload udev rules (as above)
2. Unplug and replug the Stream Deck
3. Log out and log back in (if you added yourself to plugdev group)

### Step 5: Verify USB Access

```bash
# Check if Stream Deck is accessible
lsusb | grep -i elgato

# Test with Python (in virtual environment)
source venv/bin/activate
python3 -c "from StreamDeck.DeviceManager import DeviceManager; print('Stream Deck library OK')"
```

---

## MIDI Setup

### Step 1: Connect MIDI Device

1. **USB MIDI Connection**:
   - Connect Ketron EVM device via USB cable
   - OR connect USB MIDI interface

2. **Verify MIDI Device Detection**:

**Quick Check - Is the Device Connected?**

Run these commands in order to verify your Ketron EVM is detected:

```bash
# 1. Check if USB device is detected
lsusb | grep -i midi
# Should show your MIDI device (e.g., "Ketron" or "USB MIDI")

# If nothing shows, try:
lsusb
# Look for any device that might be your Ketron EVM

# 2. Check ALSA MIDI clients (most important for MIDI)
aconnect -l
# Should list MIDI clients including your Ketron device
# Look for entries like:
#   client X: 'Ketron EVM' [type=kernel]
#   client X: 'USB MIDI Device' [type=kernel]

# 3. List ALSA MIDI ports
amidi -l
# Should show MIDI ports like:
#   hw:1,0,0  USB MIDI Device MIDI 1

# 4. Check if device appears in /dev
ls -la /dev/snd/
# Should show MIDI devices (if using ALSA)
```

**What to Look For:**

- **USB Detection**: `lsusb` should show your device
- **ALSA MIDI Client**: `aconnect -l` should show a client for your Ketron
- **MIDI Ports**: `amidi -l` should list available MIDI ports

**If Device is Not Detected:**

```bash
# Check USB connection
dmesg | tail -20
# Look for USB device connection/disconnection messages

# Check if USB device is powered
lsusb -v | grep -i "ketron\|midi"
# Shows detailed USB device information

# Verify USB cable is working (try different USB port)
# Some USB ports on Raspberry Pi may not provide enough power
```

**Using Python to List MIDI Ports (Application Method):**

```bash
# Navigate to project directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# List all available MIDI ports
python3 tests/list_midi_ports.py

# This will show output like:
# Available MIDI output ports:
#   0: MidiView 1
#   1: USB MIDI Device MIDI 1
#   2: Ketron EVM MIDI 1
```

**Test MIDI Communication:**

Once the device is detected, test if you can communicate with it:

```bash
# Navigate to project directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Test MIDI communication (replace with your actual port name)
python3 tests/devdeck/ketron/test_ketron_sysex.py "USB MIDI Device MIDI 1"
# Or try:
python3 tests/devdeck/ketron/test_ketron_sysex.py "Ketron EVM MIDI 1"
```

**Detect Ketron Event Using MIDI Identity Request:**

The Ketron Event can be detected by sending a MIDI Universal System Exclusive (SysEx) Identity Request. This is the most reliable way to verify the device is connected and responding:

```bash
# Navigate to project directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Run identity detection test
python3 tests/devdeck/ketron/test_ketron_identity.py

# Or specify a port name:
python3 tests/devdeck/ketron/test_ketron_identity.py "USB MIDI Device MIDI 1"
```

This test:
1. Sends a MIDI Universal Identity Request (F0 7E 7F 06 01 F7) to all devices
2. Listens for identity responses
3. Parses the responses to identify connected devices
4. Checks port names for "Ketron" or "Event" indicators
5. Reports if a Ketron Event is detected

**What the Identity Request Does:**

- **Sends**: Universal MIDI Identity Request message (standard MIDI protocol)
- **Receives**: Device identity response with manufacturer ID and device information
- **Identifies**: Ketron devices by their response and/or port name

This is the standard way MIDI devices identify themselves and is more reliable than just checking port names.

**Common Issues:**

- **Device not showing in `aconnect -l`**: USB MIDI driver may not be loaded, try: `sudo modprobe snd-usb-audio`
- **Permission denied**: User may not be in `audio` group: `sudo usermod -a -G audio $USER` (then log out and back in)
- **Device appears but can't connect**: Check port name matches exactly (case-sensitive)

### Step 2: Test MIDI Communication

```bash
# Navigate to project root directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Test MIDI port listing (must be run from project root)
python3 tests/list_midi_ports.py

# Test MIDI communication
python3 tests/devdeck/ketron/test_ketron_sysex.py
```

### Step 3: Identify MIDI Port Name

```bash
# Ensure you're in project root directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Run MIDI port listing script (must be run from project root)
python3 tests/list_midi_ports.py

# Note the exact port name for your Ketron device
# Example: "MidiView 1" or "Ketron EVM MIDI 1"
```

### Common MIDI Port Names on Raspberry Pi

- USB MIDI devices often appear as: `"USB MIDI Device"` or device-specific names
- ALSA MIDI ports: `"MidiView 1"`, `"MidiView 2"`, etc.
- Check with `aconnect -l` for ALSA client names

### Quick Reference: Verifying Ketron EVM MIDI Connection

**Run these commands in order to check if your Ketron EVM is connected:**

```bash
# 1. Check USB connection (quickest check)
lsusb | grep -i midi
# OR just:
lsusb
# Look for your Ketron device in the list

# 2. Check ALSA MIDI clients (most reliable for MIDI)
aconnect -l
# Should show your Ketron device as a MIDI client
# Example output:
#   client 20: 'USB MIDI Device' [type=kernel,card=1]
#   client 20: 'Ketron EVM' [type=kernel,card=1]

# 3. List MIDI ports
amidi -l
# Should show available MIDI ports

# 4. Use Python to list ports (application method)
cd ~/devdeck
source venv/bin/activate
python3 tests/list_midi_ports.py
# Shows ports in the format your application uses

# 5. Detect Ketron Event using MIDI Identity Request (most reliable)
cd ~/devdeck
source venv/bin/activate
python3 tests/devdeck/ketron/test_ketron_identity.py
# Sends MIDI Universal Identity Request and listens for responses
# This is the standard way MIDI devices identify themselves
```

**Expected Output When Connected:**

- `lsusb`: Shows USB device (may or may not say "MIDI" explicitly)
- `aconnect -l`: Shows MIDI client (e.g., "USB MIDI Device" or "Ketron EVM")
- `amidi -l`: Shows MIDI ports (e.g., "hw:1,0,0 USB MIDI Device MIDI 1")
- Python script: Shows port names your application can use

**If Nothing Shows:**

1. Check USB cable is securely connected
2. Try a different USB port on the Raspberry Pi
3. Check if device needs external power
4. Verify USB cable is data-capable (not charge-only)
5. Check dmesg for connection errors: `dmesg | tail -30`

---

## Application Configuration

### Step 1: Configure Stream Deck Serial Number

```bash
# Edit settings file
nano config/settings.yml
```

Find your Stream Deck serial number:
```bash
# In virtual environment
source venv/bin/activate

# Run a test to find serial number
python3 -c "from StreamDeck.DeviceManager import DeviceManager; decks = DeviceManager().enumerate(); print([d.get_serial_number() for d in decks])"
```

Update `settings.yml`:
```yaml
decks:
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: YOUR_SERIAL_NUMBER_HERE
  settings:
    # ... rest of configuration
```

### Step 2: Verify Key Mappings

```bash
# Check key mappings file
cat config/key_mappings.json | python3 -m json.tool

# Ensure file is valid JSON
```

### Step 3: Test Application Startup

```bash
# Activate virtual environment
source venv/bin/activate

# Test run with GUI (default)
python3 -m devdeck.main

# Or test without GUI
python3 -m devdeck.main --no-gui

# Press Ctrl+C to stop
```

**Note**: The GUI will open automatically if you have a display connected. If running headless or via SSH without X11, use the `--no-gui` flag. See the [GUI Control Panel](#gui-control-panel) section for more details.

### Step 4: Configure Screen Saver (Optional)

The application includes a screen saver feature that activates after a period of inactivity. When active, the screen brightness is dimmed to preserve the display and reduce power consumption.

**Default Behavior:**
- Screen saver activates after **30 minutes** of inactivity (no key presses)
- Brightness dims to 5% (from default 50%)
- Any key press immediately wakes the display and restores normal operation

**Configuration:**

To customize the screen saver timeout, add `screen_saver_timeout` to your deck settings in `settings.yml`:

```yaml
decks:
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: YOUR_SERIAL_NUMBER_HERE
  settings:
    screen_saver_timeout: 300  # Timeout in seconds (e.g., 300 = 5 minutes)
    controls:
      # ... rest of configuration
```

**Configuration Options:**
- `screen_saver_timeout` (optional): Time in seconds before screen saver activates
  - Default: 1800 seconds (30 minutes) if not specified
  - Recommended values: 300-3600 seconds (5-60 minutes) for production use
  - Set to 15-60 seconds for testing/debugging

**How It Works:**
1. The application tracks the last time any key was pressed
2. After the timeout period, the screen saver activates:
   - Brightness is reduced to 5%
3. Pressing any key immediately:
   - Restores original brightness
   - Re-renders the active deck
   - Resets the idle timer

**Example Configurations:**

```yaml
# Quick timeout for testing (15 seconds)
settings:
  screen_saver_timeout: 15

# Short timeout (1 minute)
settings:
  screen_saver_timeout: 60

# Medium timeout (5 minutes)
settings:
  screen_saver_timeout: 300

# Default timeout (30 minutes) - used if not specified
settings:
  screen_saver_timeout: 1800

# Long timeout (1 hour)
settings:
  screen_saver_timeout: 3600

# Disable screen saver (set to very high value)
settings:
  screen_saver_timeout: 86400  # 24 hours (effectively disabled)
```

**Note:** The screen saver helps preserve the Stream Deck display by reducing brightness during periods of inactivity. The system remains fully functional and ready to use - simply press any key to wake the display.

---

## GUI Control Panel

The application includes a graphical user interface (GUI) that provides easy control and monitoring of the EVMDeck application. The GUI is designed to work on Raspberry Pi with a 480x272 pixel display resolution, making it perfect for small touchscreen displays.

### GUI Features

The GUI Control Panel provides:

- **Application Control**: Start and exit the application with button controls
- **Status Display**: Real-time status indicator showing "Running" or "Stopped"
- **USB Device Detection**: Shows detected USB input (Elgato Stream Deck) and USB output (MIDI device) with vendor names
- **Key Press Monitor**: Real-time display of Stream Deck key presses with:
  - Timestamp for each key press
  - Key name (e.g., "Fill", "Break", "Start/Stop")
  - MIDI message in hex format (SysEx or CC messages)
- **Device Refresh**: Button to refresh USB device detection without restarting

### Prerequisites for GUI

#### 1. Install tkinter

The GUI requires `tkinter`, which may not be installed by default on Raspberry Pi OS Lite:

```bash
# Install Python tkinter package
sudo apt-get update
sudo apt-get install -y python3-tk
```

#### 2. Verify tkinter Installation

Test that tkinter is available:

```bash
python3 -c "import tkinter; print('✓ tkinter is available')"
```

If this command succeeds, tkinter is properly installed. If it fails, install it using the command above.

#### 3. Display Requirements

The GUI requires a graphical display:

- **Direct Display**: Connect a monitor, TV, or touchscreen display directly to the Raspberry Pi
- **VNC**: Use VNC server for remote desktop access
- **X11 Forwarding**: If using SSH, enable X11 forwarding (not recommended for production)

**Note**: The GUI window is sized at 480x272 pixels, which matches common small Raspberry Pi touchscreen displays.

### Running the Application with GUI

#### Method 1: Default (GUI Enabled)

The application starts with GUI by default:

```bash
# Activate virtual environment
cd ~/devdeck
source venv/bin/activate

# Run application (GUI starts automatically)
python3 -m devdeck.main
```

The GUI window will open automatically when the application starts.

#### Method 2: Without GUI

If you prefer to run without the GUI (e.g., for headless operation or as a service):

```bash
# Run without GUI
python3 -m devdeck.main --no-gui
```

### Using the GUI

#### Application Control Section

1. **Start Button**: Click to start the EVMDeck application
   - The Stream Deck will initialize and display your configured buttons
   - Status changes to "Status: Running" (green)
   - MIDI monitoring starts automatically

2. **Exit Button**: Click to exit the application
   - Stops the EVMDeck application gracefully
   - Closes the GUI window
   - Same as clicking the window's X button

3. **Status Indicator**: Shows current application state
   - "Status: Running" (green) - Application is active
   - "Status: Stopped" (red) - Application is not running

#### USB Devices Section

Displays detected USB devices:

- **USB Input Device**: Shows the Elgato Stream Deck with vendor name
  - Example: "Elgato Stream Deck MK.2"
  - Shows "None" if not detected

- **USB Output Device**: Shows the MIDI output device with vendor name
  - Example: "CH345 MIDI 1" or "Ketron MIDI Device"
  - Shows "None" if not detected

- **Refresh Devices Button**: Click to scan for USB devices again
  - Useful after connecting/disconnecting devices
  - Updates the display without restarting the application

#### Keys Monitor Section

Displays real-time Stream Deck key presses:

- **Format**: `[HH:MM:SS] Pressed KeyName [MIDI Hex]`
- **Example Messages**:
  - `[14:23:45] Pressed Fill [F0 26 79 03 15 7F F7]` (SysEx message)
  - `[14:23:46] Pressed Voice1 [BF 72 40]` (CC message)
  - `[14:23:47] Pressed Volume Up [BF 6C 41]` (Volume CC message)

- **MIDI Message Types**:
  - **SysEx Messages**: Full hex string including F0 (start) and F7 (end)
  - **CC Messages**: Format `Bn CC VV` where:
    - `Bn` = Status byte (B0-BF for channels 1-16)
    - `CC` = Control change number
    - `VV` = Value (0-127)

- **Scrolling**: The monitor automatically scrolls to show the most recent key presses
- **Limited History**: Shows approximately the last 50 key presses

### GUI Troubleshooting

#### Issue: GUI Window Doesn't Appear

**Symptoms**: Application starts but no GUI window opens

**Solutions**:

1. **Check tkinter availability**:
   ```bash
   python3 -c "import tkinter; print('tkinter OK')"
   ```
   If this fails, install tkinter: `sudo apt-get install python3-tk`

2. **Verify display is available**:
   ```bash
   echo $DISPLAY
   ```
   Should show something like `:0` or `:0.0`. If empty, you may be in a headless environment.

3. **Check if running via SSH without X11**:
   - GUI requires a display connection
   - Use VNC or connect directly to a monitor
   - Or run with `--no-gui` flag

4. **Verify you're not in a service/daemon context**:
   - Services typically don't have display access
   - Run manually from a terminal session to test GUI

#### Issue: "No module named 'tkinter'" Error

**Solution**: Install tkinter package:
```bash
sudo apt-get update
sudo apt-get install -y python3-tk
```

#### Issue: GUI Window is Too Small or Too Large

**Solution**: The GUI is optimized for 480x272 pixel displays. You can resize the window manually, but the layout is designed for this resolution.

#### Issue: USB Devices Show "None" or "Unknown Device"

**Solutions**:

1. **Click "Refresh Devices"** button to rescan
2. **Verify devices are connected**:
   ```bash
   lsusb | grep -i elgato  # Stream Deck
   lsusb | grep -i midi   # MIDI device
   ```
3. **Check USB permissions** (see [USB Permissions Configuration](#usb-permissions-configuration) section)

#### Issue: Key Presses Not Showing in Monitor

**Solutions**:

1. **Ensure application is started**: Click "Start" button first
2. **Check that MIDI monitoring started**: Should see "[timestamp] EVM Deck application ready" message
3. **Verify Stream Deck is working**: Press keys and check if they appear in the monitor
4. **Check for errors**: Look at terminal output for any error messages

### GUI and Service Mode

**Important**: The GUI is designed for interactive use. When running as a systemd service (see [Running as a Service](#running-as-a-service) section), you should use the `--no-gui` flag:

```bash
# In systemd service file
ExecStart=/home/admin/devdeck/venv/bin/python3 -m devdeck.main --no-gui
```

Services typically don't have display access, so the GUI won't work in service mode. Use the GUI when running manually for testing, configuration, or monitoring.

### GUI Best Practices

1. **For Development/Testing**: Use GUI mode for easy monitoring and control
2. **For Production/Service**: Use `--no-gui` mode when running as a service
3. **Display Setup**: Use a small touchscreen (480x272) for the best experience
4. **Remote Access**: Use VNC if you need GUI access remotely
5. **Performance**: GUI adds minimal overhead; suitable for Raspberry Pi 5

---

## Samba Configuration (Windows Network Access)

This section provides detailed instructions for configuring Samba on your Raspberry Pi to enable Windows file sharing for the `~/devdeck` directory. This allows you to access and edit files directly from your Windows machine over the network.

### Step 1: Install Samba

```bash
# Update package lists
sudo apt update

# Install Samba and related tools
sudo apt install -y samba samba-common-bin
```

### Step 2: Configure Samba Share for ~/devdeck

**Option A: Secure Configuration (Recommended - Requires Password)**

This option requires authentication but is more secure:

```bash
# Backup the original Samba configuration
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.backup

# Edit Samba configuration
sudo nano /etc/samba/smb.conf
```

**First, check the `[global]` section** (at the top of the file) and ensure it has:

```ini
[global]
   server min protocol = SMB2
   server max protocol = SMB3
```

If these lines don't exist, add them to the `[global]` section. This ensures Windows 10/11 compatibility.

**Then, add the following configuration at the end of the file** (replace `admin` with your actual username):

```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin
   create mask = 0664
   directory mask = 0775
   force user = admin
   force group = admin
```

**Important**: 
- Replace `admin` with your actual username. You can find your username with: `whoami`
- **If you get "NT_STATUS_NO_SUCH_GROUP" error**: The `force group = admin` line requires that a group named `admin` exists. You can either:
  - Create the group: `sudo groupadd admin` (if it doesn't exist)
  - Or remove the `force group = admin` line from the config (Samba will use the user's default group)

**Option B: Guest Access (Less Secure - No Password Required)**

If you prefer guest access without a password (only recommended for trusted local networks):

```bash
# Edit Samba configuration
sudo nano /etc/samba/smb.conf
```

Add the following configuration at the end of the file (replace `admin` with your actual username):

```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   guest ok = yes
   create mask = 0664
   directory mask = 0775
   force user = admin
   force group = admin
```

**Important**: 
- Replace `admin` with your actual username. You can find your username with: `whoami`
- **If you get "NT_STATUS_NO_SUCH_GROUP" error**: The `force group = admin` line requires that a group named `admin` exists. You can either:
  - Create the group: `sudo groupadd admin` (if it doesn't exist)
  - Or remove the `force group = admin` line from the config (Samba will use the user's default group)

**Important Notes:**
- **Replace `admin` with your actual username** in all configuration examples above
- Find your username: `whoami`
- Option A (secure) is recommended for production use
- Option B (guest) is convenient but less secure
- The `create mask = 0664` allows the owner and group to write files (needed for config files)

### Step 3: Set Samba User Password (For Secure Configuration)

If you chose Option A (secure configuration), set a Samba password for your user:

```bash
# Set Samba password for your user (replace 'admin' with your username)
sudo smbpasswd -a admin
```

You'll be prompted to enter a password. This password is separate from your Linux user password and is used specifically for Samba access.

**Note**: If the user doesn't exist in Samba yet, you may need to enable the user:

```bash
# Enable Samba user (replace 'admin' with your username)
sudo smbpasswd -e admin
```

**Find your username:**
```bash
whoami
```

### Step 3a: Adding Additional Samba Users or Changing Users

If you want to add a different user (e.g., `pi` instead of `admin`) or add multiple users:

**Adding a New Samba User:**

```bash
# Add a new Samba user (e.g., 'pi')
sudo smbpasswd -a pi

# You'll be prompted to enter a password twice
# This password is separate from the Linux user password

# Enable the user
sudo smbpasswd -e pi

# Verify the user was added
sudo pdbedit -L
# Should show both users: admin and pi
```

**Updating Samba Configuration for New User:**

If you want to change the share to use a different user (e.g., `pi` instead of `admin`):

```bash
# Edit Samba config
sudo nano /etc/samba/smb.conf
```

Update the `[devdeck]` section to use the new user:

```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/pi/devdeck          ← Change to new user's home directory
   browseable = yes
   writeable = yes
   valid users = pi                 ← Change to new username
   create mask = 0664
   directory mask = 0775
   force user = pi                  ← Change to new username
   # force group = pi               ← Optional: change if needed
```

**Important**: If changing users, also update:
1. **Directory path**: Change `/home/admin/devdeck` to `/home/pi/devdeck` (or new user's path)
2. **Directory ownership**: 
   ```bash
   sudo chown -R pi:pi /home/pi/devdeck
   ```
3. **Directory permissions**:
   ```bash
   find /home/pi/devdeck -type d -exec chmod 755 {} \;
   find /home/pi/devdeck -type f -exec chmod 664 {} \;
   ```

**Allowing Multiple Users:**

If you want multiple users to access the share:

```bash
# Add multiple users
sudo smbpasswd -a admin
sudo smbpasswd -a pi

# Enable both
sudo smbpasswd -e admin
sudo smbpasswd -e pi
```

Then in `smb.conf`, list all users:

```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin, pi          ← List all allowed users
   create mask = 0664
   directory mask = 0775
   force user = admin               ← Files will be owned by this user
```

**Managing Samba Users:**

```bash
# List all Samba users
sudo pdbedit -L

# View detailed user information
sudo pdbedit -L -v username

# Change a user's password
sudo smbpasswd username

# Disable a user (prevent login but keep account)
sudo smbpasswd -d username

# Enable a user
sudo smbpasswd -e username

# Delete a Samba user (doesn't delete Linux user)
sudo smbpasswd -x username
```

**Restart Samba after making changes:**

```bash
sudo systemctl restart smbd
```

### Step 4: Verify Directory Permissions

Ensure the `~/devdeck` directory has proper permissions. **Important**: Config files must be writable by the application:

```bash
# Check current permissions
ls -la ~/devdeck

# Set ownership (if needed)
# $USER is a shell variable that automatically expands to your current username
# So if you're logged in as 'admin', $USER will be 'admin'
# You do NOT need to replace $USER with your username - it's automatic!
sudo chown -R $USER:$USER ~/devdeck

# Alternative: If $USER doesn't work, you can use your username directly:
# sudo chown -R admin:admin ~/devdeck
# (Replace 'admin' with your actual username if different)

# Set directory permissions (directories need execute permission)
find ~/devdeck -type d -exec chmod 755 {} \;

# Set file permissions (files need read/write for owner, read for group)
find ~/devdeck -type f -exec chmod 664 {} \;

# Make scripts executable
find ~/devdeck -name "*.sh" -exec chmod 755 {} \;

# Verify config files are writable
ls -la ~/devdeck/config/
# Should show: -rw-rw-r-- for files (664 permissions)
```

**Critical**: The application needs to write to `config/key_mappings.json` and other config files. Files must have `664` permissions (read/write for owner, read for group), not `644` (read-only for owner).

### Step 5: Test Samba Configuration

```bash
# Test Samba configuration file syntax
sudo testparm

# Or get a cleaner summary (suppresses warnings)
sudo testparm -s

# View just the devdeck share configuration
sudo testparm -s | grep -A 15 "\[devdeck\]"
```

**What to Look For in testparm Output:**

For the `[devdeck]` share, you should see:

```
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   read only = No          ← This means writable (good!)
   valid users = admin
   create mask = 0664
   directory mask = 0775
   force user = admin
   force group = admin
```

**Key Settings Explained:**

- **`read only = No`** ✅ **This is correct!** This means the share is writable (not read-only). This is what you want.
- **`browseable = yes`** ✅ Share is visible in network browser
- **`valid users = admin`** ✅ Your username is allowed to access
- **`create mask = 0664`** ✅ New files will be readable/writable by owner
- **`directory mask = 0775`** ✅ New directories will have proper permissions
- **`force user = admin`** ✅ Files created via Samba will be owned by your user

**If you see `read only = Yes`**, the share is read-only and you need to fix it:
```bash
# Check your smb.conf file
sudo nano /etc/samba/smb.conf
# Make sure the [devdeck] section has: writeable = yes
# Or: read only = no
# Then restart: sudo systemctl restart smbd
```

**Note**: If testparm shows warnings, they're usually safe to ignore. Errors need to be fixed before proceeding.

### Step 6: Restart Samba Service

```bash
# Restart Samba service to apply changes
sudo systemctl restart smbd

# Enable Samba to start on boot (optional)
sudo systemctl enable smbd

# Check service status
sudo systemctl status smbd
```

### Step 7: Find Raspberry Pi IP Address

You'll need your Raspberry Pi's IP address to connect from Windows:

```bash
# Find IP address
hostname -I

# Or get more detailed information
ip addr show | grep "inet "

# Note the IP address (e.g., 192.168.1.100)
```

**Write down this IP address** - you'll need it in the next step!

### Step 8: Configure Windows to Access the Share

Follow these steps on your **Windows computer** to access the Raspberry Pi's `devdeck` directory:

#### Prerequisites (Get from Raspberry Pi)

Before starting, you need:
1. **Raspberry Pi IP address** (from Step 7 above, e.g., `192.168.1.100`)
2. **Your Raspberry Pi username** (run `whoami` on Pi, e.g., `admin`)
3. **Samba password** (the password you set with `sudo smbpasswd -a admin`)

#### Quick Access Method (Temporary Connection)

**Easiest way to access the share:**

1. **Press `Windows Key + R`** to open Run dialog
2. **Type**: `\\192.168.1.100\devdeck` (replace `192.168.1.100` with your Pi's IP)
3. **Press Enter**
4. **Enter credentials** when prompted:
   - **Username**: `admin` (replace with your Pi username - use just the username, NOT `WORKGROUP\admin`)
   - **Password**: Your Samba password
   - **Check "Remember my credentials"** if you want Windows to save it
   - **If you get "group name not found" error**: Try `WORKGROUP\admin` or just `admin` (without any prefix)
5. **Click OK**

You should now see the `devdeck` folder contents in File Explorer!

**Important**: Make sure you're connecting to `\\IP\devdeck` directly, NOT `\\IP\admin` or browsing through a parent folder. If you see both `admin` and `devdeck` folders, you're in the wrong location - connect directly to `\\IP\devdeck` instead.

**Troubleshooting**: If you get a "group name not found" error, see the [troubleshooting section](#group-name-not-found-error) below. Common fixes: use just the username (not `WORKGROUP\username`), or verify the Samba user exists with `sudo pdbedit -L` on the Pi.

**Note**: This connection is temporary and will disconnect when you close File Explorer or restart Windows.

#### Method 1: Using File Explorer Address Bar (Recommended for Quick Access)

1. **Open File Explorer** (press `Windows Key + E`)
2. **Click in the address bar** at the top (or press `Ctrl + L`)
3. **Type**: `\\192.168.1.100\devdeck`
   - Replace `192.168.1.100` with your Raspberry Pi's IP address
   - Example: `\\192.168.1.100\devdeck`
4. **Press Enter**
5. **Enter credentials** when Windows prompts:
   - **Username**: `admin` (replace with your Pi username from `whoami`)
   - **Password**: Your Samba password (set with `sudo smbpasswd -a admin`)
   - **Check "Remember my credentials"** to save for future access
6. **Click OK**

You should now see the contents of `~/devdeck` from your Raspberry Pi!

**Tip**: You can bookmark this location by dragging it to your Quick Access toolbar.

#### Method 2: Map Network Drive (Permanent Connection - Recommended)

This creates a permanent drive letter (like `Z:`) that stays connected:

1. **Open File Explorer** (press `Windows Key + E`)
2. **Right-click "This PC"** in the left sidebar
   - If you don't see "This PC", click "View" → "Show" → "Navigation pane"
3. **Select "Map network drive..."** from the context menu
4. **Choose a drive letter** from the dropdown (e.g., `Z:`)
5. **Enter folder path**: `\\192.168.1.100\devdeck`
   - Replace `192.168.1.100` with your Raspberry Pi's IP address
6. **Check "Reconnect at sign-in"** ✓ (this makes it permanent)
7. **Check "Connect using different credentials"** ✓ (if using secure Samba config)
8. **Click "Finish"**
9. **Enter credentials** when prompted:
   - **Username**: `admin` (replace with your Pi username)
   - **Password**: Your Samba password
   - **Check "Remember my credentials"** ✓
10. **Click OK**

The drive will now appear as `Z:` (or your chosen letter) in File Explorer under "This PC" → "Network locations". It will automatically reconnect every time you sign in to Windows!

**To disconnect later**: Right-click the drive → "Disconnect"

#### Method 3: Using PowerShell/Command Prompt

For command-line users or scripting:

1. **Open PowerShell** (press `Windows Key + X` → "Windows PowerShell" or "Terminal")
2. **Run this command** (replace with your details):
   ```powershell
   net use Z: \\192.168.1.100\devdeck /user:admin /persistent:yes
   ```
   - Replace `192.168.1.100` with your Pi's IP address
   - Replace `admin` with your Pi username
   - Replace `Z:` with your preferred drive letter
3. **Enter password** when prompted
4. The drive is now mapped and will persist across reboots

**If you get "System error 2220 - The group name could not be found":**
- Try: `net use Z: \\192.168.1.100\devdeck /user:WORKGROUP\admin /persistent:yes`
- Or verify the Samba user exists on Pi: `sudo pdbedit -L` (should show your username)
- See [troubleshooting section](#group-name-not-found-error) for more solutions

**To disconnect later:**
```powershell
net use Z: /delete
```

**To list all mapped drives:**
```powershell
net use
```

#### Quick Reference: Windows Access Summary

**What you need:**
- Raspberry Pi IP address (e.g., `192.168.1.100`)
- Your Pi username (e.g., `admin` - find with `whoami` on Pi)
- Samba password (set with `sudo smbpasswd -a admin` on Pi)

**Quickest way to connect:**
1. Press `Windows Key + R`
2. Type: `\\192.168.1.100\devdeck` (replace with your Pi's IP)
3. Press Enter
4. Enter username and Samba password

**For permanent access:**
- Use Method 2 (Map Network Drive) to create a drive letter that stays connected

**Connection path format:**
- `\\IP-ADDRESS\devdeck` (e.g., `\\192.168.1.100\devdeck`)
- Or `\\HOSTNAME\devdeck` (e.g., `\\raspberrypi\devdeck`)

**⚠️ Important**: Connect directly to `\\IP\devdeck`, NOT `\\IP\admin` or through a parent folder. If you see both `admin` and `devdeck` folders, you're in the wrong location - use the direct path above.

### Step 9: Access by Hostname (Optional)

Instead of using an IP address, you can use the Raspberry Pi's hostname:

```bash
# On Raspberry Pi, check hostname
hostname

# Example output: raspberrypi
```

Then on Windows, use: `\\raspberrypi\devdeck` (or whatever your hostname is)

**Note**: Hostname resolution may not work on all networks. If it doesn't work, use the IP address instead.

### Step 10: Mount Samba Share on Linux (Alternative Method)

If you're accessing the Samba share from another Linux machine (including another Raspberry Pi), you can mount it using CIFS:

**Install CIFS Utilities:**

```bash
# On the Linux machine that will mount the share
sudo apt update
sudo apt install -y cifs-utils
```

**Create Mount Point:**

```bash
# Create directory for mounting
sudo mkdir -p /mnt/devdeck
```

**Mount the Share:**

```bash
# Method 1: Mount with password prompt (most secure)
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=admin,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775

# Enter password when prompted

# Method 2: Mount with password in command (less secure, but convenient)
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=admin,password=YOUR_PASSWORD,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775

# Method 3: Mount with credentials file (more secure than Method 2)
# First, create credentials file:
echo "username=admin" | sudo tee /root/.devdeck_credentials
echo "password=YOUR_PASSWORD" | sudo tee -a /root/.devdeck_credentials
sudo chmod 600 /root/.devdeck_credentials

# Then mount:
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o credentials=/root/.devdeck_credentials,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
```

**Important Options Explained:**

- `username=admin`: Your Samba username
- `password=YOUR_PASSWORD`: Your Samba password (use credentials file for security)
- `uid=$(id -u)`: Mount as your user ID (so files are owned by you)
- `gid=$(id -g)`: Mount with your group ID
- `iocharset=utf8`: Support UTF-8 filenames
- `file_mode=0664`: File permissions (read/write for owner and group)
- `dir_mode=0775`: Directory permissions

**Unmount the Share:**

```bash
sudo umount /mnt/devdeck
```

**Auto-Mount on Boot (Optional):**

Add to `/etc/fstab`:

```bash
sudo nano /etc/fstab
```

Add this line (replace with your details):

```
//10.0.0.51/devdeck /mnt/devdeck cifs credentials=/root/.devdeck_credentials,uid=1000,gid=1000,iocharset=utf8,file_mode=0664,dir_mode=0775 0 0
```

**Troubleshooting CIFS Mount Errors:**

**Error: "mount error(22): Invalid argument"**

This usually means a syntax error in the mount command. Common fixes:

1. **Check password syntax**: Use `password=YOUR_PASSWORD`, not `username=admin,YOUR_PASSWORD`
   ```bash
   # WRONG:
   sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck -o username=admin,aminnie123,...
   
   # CORRECT:
   sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck -o username=admin,password=aminnie123,...
   ```

2. **Verify mount point exists**:
   ```bash
   sudo mkdir -p /mnt/devdeck
   ```

3. **Check if cifs-utils is installed**:
   ```bash
   dpkg -l | grep cifs-utils
   # If not installed:
   sudo apt install cifs-utils
   ```

4. **Try with SMB version specified**:
   ```bash
   sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
     -o username=admin,password=YOUR_PASSWORD,vers=3.0,uid=$(id -u),gid=$(id -g),iocharset=utf8
   ```

5. **Check kernel messages for details**:
   ```bash
   dmesg | tail -20
   # Look for CIFS-related error messages
   ```

6. **Test with minimal options first**:
   ```bash
   # Start simple, then add options
   sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck -o username=admin
   # Enter password when prompted
   # If this works, add other options one by one
   ```

**Error: "mount error(13): Permission denied"**

This error means authentication failed or the user doesn't have permission. Try these fixes:

**Fix 1: Verify Samba User Exists and is Enabled**

On the Raspberry Pi (the Samba server), check:

```bash
# List all Samba users
sudo pdbedit -L

# Should show: admin (or your username)
# If your user is NOT listed, add it:
sudo smbpasswd -a admin
# Enter password twice

# Enable the user (if disabled):
sudo smbpasswd -e admin

# Verify user is enabled:
sudo pdbedit -L -v admin
# Should show account flags: [U] (User account)
```

**Fix 2: Verify Password is Correct**

The password you enter must be the **Samba password**, not your Linux user password:

```bash
# On Raspberry Pi, reset Samba password if needed:
sudo smbpasswd admin
# Enter new password twice
```

**Fix 3: Check Samba Share Configuration**

On Raspberry Pi, verify the share allows your user:

```bash
# Check Samba configuration
sudo testparm -s | grep -A 10 "\[devdeck\]"
```

Should show:
```
[devdeck]
   valid users = admin    ← Your username should be here
   read only = No
   writeable = yes
```

If `valid users` doesn't include your username, edit `/etc/samba/smb.conf`:

```bash
sudo nano /etc/samba/smb.conf
```

In the `[devdeck]` section, ensure:
```ini
[devdeck]
   valid users = admin
   # Or for multiple users: valid users = admin, pi
```

Then restart:
```bash
sudo systemctl restart smbd
```

**Fix 4: Try with Workgroup/Domain Prefix**

Sometimes you need to specify the workgroup:

```bash
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=WORKGROUP\\admin,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
# Note: Use double backslash \\ for workgroup prefix
```

Or with domain= option:
```bash
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=admin,domain=WORKGROUP,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
```

**Fix 5: Try Guest Access (If Enabled)**

If guest access is enabled on the share, try mounting without credentials:

```bash
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o guest,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
```

**Fix 6: Check SMB Protocol Version**

Try specifying SMB version explicitly:

```bash
# Try SMB 3.0
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=admin,vers=3.0,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775

# Or try SMB 2.1
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o username=admin,vers=2.1,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
```

**Fix 7: Test Samba Share from Raspberry Pi**

On the Raspberry Pi, test if the share works locally:

```bash
# Test accessing the share
smbclient //localhost/devdeck -U admin
# Enter Samba password
# Type 'ls' to list files
# Type 'exit' to quit
```

If this works, the share is configured correctly and the issue is with the mount command or network.

**Fix 8: Check Network Connectivity and Firewall**

```bash
# Test connectivity
ping 10.0.0.51

# Test SMB port
telnet 10.0.0.51 445
# Or:
nc -zv 10.0.0.51 445

# On Raspberry Pi, check firewall
sudo ufw status
# If firewall is active, ensure Samba is allowed:
sudo ufw allow samba
```

**Fix 9: Use Credentials File**

Create a credentials file for more reliable authentication:

```bash
# Create credentials file
echo "username=admin" | sudo tee /root/.devdeck_credentials
echo "password=YOUR_SAMBA_PASSWORD" | sudo tee -a /root/.devdeck_credentials
echo "domain=WORKGROUP" | sudo tee -a /root/.devdeck_credentials
sudo chmod 600 /root/.devdeck_credentials

# Mount using credentials file
sudo mount -t cifs //10.0.0.51/devdeck /mnt/devdeck \
  -o credentials=/root/.devdeck_credentials,uid=$(id -u),gid=$(id -g),iocharset=utf8,file_mode=0664,dir_mode=0775
```

**Fix 10: Check Kernel Messages**

For more details on the error:

```bash
# Check kernel messages
dmesg | tail -30
# Look for CIFS-related error messages

# Check system logs
sudo journalctl -xe | tail -30
```

**Most Common Causes:**

1. **Samba user doesn't exist**: Run `sudo smbpasswd -a admin` on Raspberry Pi
2. **Wrong password**: Use the Samba password (set with `smbpasswd`), not Linux password
3. **User not in valid_users**: Check `valid users = admin` in smb.conf
4. **SMB version mismatch**: Try adding `vers=3.0` or `vers=2.1` to mount options

**Error: "Host is down" or "Connection refused"**

- Verify Raspberry Pi is accessible: `ping 10.0.0.51`
- Check Samba service is running: `sudo systemctl status smbd` on Pi
- Verify firewall allows SMB: `sudo ufw allow samba` on Pi

### Step 11: Verify Access

Test that you can read and write files:

1. **From Windows**: Create a test file in the mapped drive
2. **On Raspberry Pi**: Verify the file appears:
   ```bash
   ls -la ~/devdeck/test.txt
   ```
3. **From Windows**: Edit a file (e.g., `config/settings.yml`)
4. **On Raspberry Pi**: Verify changes are saved:
   ```bash
   cat ~/devdeck/config/settings.yml
   ```

### Troubleshooting Samba Access

#### Quick Fix: Permission Denied After Samba Setup

**If you're seeing `[Errno 13] Permission denied: '/home/admin/devdeck/config/key_mappings.json'` errors**, run these commands immediately:

```bash
# 1. Find your username
whoami

# 2. Fix ownership (replace 'admin' with your username if different)
sudo chown -R $USER:$USER ~/devdeck

# 3. Fix directory permissions
find ~/devdeck -type d -exec chmod 755 {} \;

# 4. Fix file permissions (664 = read/write for owner, read for group)
find ~/devdeck -type f -exec chmod 664 {} \;

# 5. Make scripts executable
find ~/devdeck -name "*.sh" -exec chmod 755 {} \;

# 6. Verify config files are writable
ls -la ~/devdeck/config/
# Should show: -rw-rw-r-- (664), NOT -rw-r--r-- (644)

# 7. Update Samba config to use your username (if needed)
# Edit /etc/samba/smb.conf and replace 'pi' with your username in the [devdeck] section
sudo nano /etc/samba/smb.conf
# Change: force user = pi  →  force user = admin (or your username)
# Change: valid users = pi  →  valid users = admin (or your username)
# Change: path = /home/pi/devdeck  →  path = /home/admin/devdeck (or your path)

# 8. Restart Samba
sudo systemctl restart smbd

# 9. Restart the application service
sudo systemctl restart devdeck.service

# 10. Check if it's working
sudo systemctl status devdeck.service
```

**Root Cause**: The `chmod 644` command in the original instructions made files read-only. Config files need `664` permissions so the application can write to them.

#### Cannot Access Share from Windows

**Problem**: Windows cannot connect to `\\raspberry-pi-ip\devdeck`

**Windows-Side Checks:**

1. **Test network connectivity** (in PowerShell):
   ```powershell
   ping 192.168.1.100
   ```
   Replace with your Pi's IP. If this fails, check network connection.

2. **Test SMB port** (in PowerShell):
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.100 -Port 445
   ```
   Should show "TcpTestSucceeded : True". If false, check firewall.

3. **Check Windows Firewall**:
   - Open "Windows Defender Firewall" → "Allow an app through firewall"
   - Ensure "File and Printer Sharing" is enabled for Private networks

4. **Try different connection method**:
   - If `\\IP\devdeck` doesn't work, try `\\raspberrypi\devdeck` (hostname)
   - Or try accessing via "Network" in File Explorer

5. **Clear Windows credentials** (if authentication keeps failing):
   - Open "Credential Manager" (search in Start menu)
   - Go to "Windows Credentials"
   - Remove any entries for your Raspberry Pi
   - Try connecting again

#### "Extended Error" When Mapping Network Drive

**Problem**: Windows shows "extended error" when trying to map the network drive

**Solution 1: Use File Explorer First (Recommended)**

Before mapping, test the connection directly:

1. **Press `Windows Key + R`**
2. **Type**: `\\192.168.1.100\devdeck` (your Pi's IP)
3. **Press Enter**
4. **Enter credentials** and connect
5. **If this works**, then try mapping the drive again

**Solution 2: Check SMB Protocol Version**

Windows 10/11 may require SMB 2.0 or higher. On Raspberry Pi:

```bash
# Check Samba version
samba --version

# Edit Samba config to ensure SMB 2.0+ is enabled
sudo nano /etc/samba/smb.conf
```

Add or verify in the `[global]` section (at the top of the file):

```ini
[global]
   server min protocol = SMB2
   server max protocol = SMB3
```

Then restart Samba:
```bash
sudo systemctl restart smbd
```

**Solution 3: Use PowerShell Instead of GUI**

Sometimes the GUI has issues, but PowerShell works:

1. **Open PowerShell as Administrator** (Right-click → "Run as administrator")
2. **Run**:
   ```powershell
   net use Z: \\192.168.1.100\devdeck /user:admin /persistent:yes
   ```
   Replace with your Pi's IP and username
3. **Enter password** when prompted
4. **Check if it worked**:
   ```powershell
   net use
   ```
   Should show `Z:` mapped

**Solution 4: Clear All Network Drive Mappings**

Sometimes old mappings cause conflicts:

1. **Open PowerShell as Administrator**
2. **List all mapped drives**:
   ```powershell
   net use
   ```
3. **Disconnect all** (if needed):
   ```powershell
   net use * /delete
   ```
4. **Try mapping again**

**Solution 5: Check Windows SMB Client**

Enable SMB 1.0 (if needed, though not recommended for security):

1. **Open "Turn Windows features on or off"** (search in Start menu)
2. **Expand "SMB 1.0/CIFS File Sharing Support"**
3. **Check "SMB 1.0/CIFS Client"** (NOT the server)
4. **Click OK** and restart if prompted
5. **Try mapping again**

**Note**: SMB 1.0 is deprecated and insecure. Only use this as a last resort.

**Solution 6: Verify Share is Accessible**

On Raspberry Pi, test the share locally:

```bash
# Test Samba share from command line
smbclient //localhost/devdeck -U admin
# Enter your Samba password
# Type 'ls' to list files
# Type 'exit' to quit

# If this works, the share is configured correctly
# The issue is likely Windows-side
```

**Solution 7: Check Windows Event Viewer**

For more details on the error:

1. **Open "Event Viewer"** (search in Start menu)
2. **Go to**: Windows Logs → System
3. **Look for errors** around the time you tried to map the drive
4. **Check the error message** for more details

**Solution 8: Try Different Drive Letter**

Sometimes a specific drive letter is in use or reserved:

1. **Try a different letter** (e.g., `X:`, `Y:`, `W:`)
2. **Or let Windows assign automatically**:
   ```powershell
   net use * \\192.168.1.100\devdeck /user:admin /persistent:yes
   ```

#### "Group Name Not Found" Error

**Problem**: Windows shows "group name not found" when trying to access `\\IP\devdeck`

This error usually means Windows is having trouble with the username format or authentication.

**Solution 1: Use Correct Username Format**

When Windows prompts for credentials, use one of these formats:

1. **Just the username** (try this first):
   - Username: `admin` (your Pi username)
   - Password: Your Samba password

2. **With workgroup prefix** (if above doesn't work):
   - Username: `WORKGROUP\admin` or `RASPBERRYPI\admin`
   - Password: Your Samba password

3. **With IP address prefix** (alternative):
   - Username: `192.168.1.100\admin` (replace with your Pi's IP)
   - Password: Your Samba password

**Solution 2: Verify Samba User Exists and is Enabled**

On Raspberry Pi, check that your user is properly set up in Samba:

```bash
# List all Samba users
sudo pdbedit -L

# Should show your username (e.g., admin)
# If your username is NOT listed, add it:
sudo smbpasswd -a admin
# Enter password twice

# Enable the user (if needed)
sudo smbpasswd -e admin

# Verify user details
sudo pdbedit -L -v admin
```

**Solution 3: Check Samba Workgroup Setting**

Windows might be looking for a different workgroup. On Raspberry Pi:

```bash
# Check current workgroup setting
sudo testparm -s | grep workgroup

# Edit Samba config
sudo nano /etc/samba/smb.conf
```

In the `[global]` section, ensure you have:

```ini
[global]
   workgroup = WORKGROUP
   server string = %h server (Samba, Ubuntu)
```

Then restart:
```bash
sudo systemctl restart smbd
```

**Solution 4: Use IP Address Instead of Hostname**

Sometimes hostname resolution causes issues. Always use the IP address:

- ✅ Use: `\\192.168.1.100\devdeck`
- ❌ Avoid: `\\raspberrypi\devdeck` (if it causes issues)

**Solution 5: Clear Windows Credentials and Retry**

Windows might have cached incorrect credentials:

1. **Open "Credential Manager"** (search in Start menu)
2. **Go to "Windows Credentials"**
3. **Find and remove** any entries for:
   - Your Raspberry Pi IP address
   - Your Raspberry Pi hostname
   - `WORKGROUP` entries
4. **Close Credential Manager**
5. **Try connecting again** with fresh credentials

**Solution 6: Use PowerShell with Explicit Credentials**

Instead of the GUI, use PowerShell with explicit credentials:

```powershell
# Method 1: Prompt for password
$cred = Get-Credential
# Enter: admin (username) and your Samba password
net use Z: \\192.168.1.100\devdeck /user:admin /persistent:yes

# Method 2: Direct command (will prompt for password)
net use Z: \\192.168.1.100\devdeck /user:admin /persistent:yes
# Enter password when prompted
```

**If you get "System error 2220 - The group name could not be found" in PowerShell:**

This error means Windows can't resolve the username/group. Try these fixes:

**Fix 1: Use Workgroup Prefix in PowerShell**
```powershell
# Try with workgroup prefix
net use Z: \\10.0.0.51\devdeck /user:WORKGROUP\admin /persistent:yes
# Enter password when prompted
```

**Fix 2: Use IP Address as Domain**
```powershell
# Try with IP as domain
net use Z: \\10.0.0.51\devdeck /user:10.0.0.51\admin /persistent:yes
# Enter password when prompted
```

**Fix 3: Verify Samba User on Raspberry Pi First**
On your Raspberry Pi, run:
```bash
# Check if user exists in Samba
sudo pdbedit -L
# Should show: admin

# If NOT listed, add the user:
sudo smbpasswd -a admin
# Enter password twice

# Enable the user:
sudo smbpasswd -e admin

# Verify it's enabled:
sudo pdbedit -L -v admin
```

**Fix 4: Check Samba Workgroup Setting**
On Raspberry Pi:
```bash
# Check workgroup
sudo testparm -s | grep workgroup

# Edit if needed
sudo nano /etc/samba/smb.conf
# In [global] section, ensure: workgroup = WORKGROUP

# Restart Samba
sudo systemctl restart smbd
```

**Fix 5: Use Different Username Format**
Try these variations in PowerShell:
```powershell
# Option A: Just username (most common)
net use Z: \\10.0.0.51\devdeck /user:admin /persistent:yes

# Option B: With workgroup
net use Z: \\10.0.0.51\devdeck /user:WORKGROUP\admin /persistent:yes

# Option C: With IP as domain
net use Z: \\10.0.0.51\devdeck /user:10.0.0.51\admin /persistent:yes

# Option D: With hostname as domain (if you know it)
net use Z: \\10.0.0.51\devdeck /user:raspberrypi\admin /persistent:yes
```

**Most Common Fix**: Run Fix 3 (verify Samba user exists) on the Pi, then try Fix 5 Option A or B in PowerShell.

**Solution 7: Check if User Group Exists**

On Raspberry Pi, verify the user's primary group exists:

```bash
# Check your user's groups
groups admin
# (Replace 'admin' with your username)

# Check if primary group exists
id admin
# Should show: uid=1000(admin) gid=1000(admin) groups=1000(admin),...

# If group doesn't exist, create it (rarely needed):
sudo groupadd admin
sudo usermod -g admin admin
```

**Solution 8: Test Samba Share from Command Line**

Verify the share works from the Pi itself:

```bash
# Test accessing the share locally
smbclient //localhost/devdeck -U admin
# Enter your Samba password
# Type 'ls' to list files
# Type 'exit' to quit

# If this works, Samba is configured correctly
# The issue is Windows authentication format
```

**If you get "NT_STATUS_NO_SUCH_GROUP" error when testing with smbclient:**

This error means Samba can't find the group specified in the configuration. Fix it with:

**Fix 1: Check User's Primary Group**

```bash
# Check your user's groups
id admin
# Should show: uid=1000(admin) gid=1000(admin) groups=1000(admin),...

# Check if the primary group exists
getent group admin
# Should show: admin:x:1000:admin

# If group doesn't exist, create it:
sudo groupadd admin
sudo usermod -g admin admin
```

**Fix 2: Remove or Fix force group Setting**

The `force group = admin` in your Samba config might be pointing to a non-existent group:

```bash
# Check current Samba config
sudo testparm -s | grep -A 10 "\[devdeck\]"

# Edit Samba config
sudo nano /etc/samba/smb.conf
```

In the `[devdeck]` section, either:

**Option A: Remove force group** (if group doesn't exist):
```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin
   create mask = 0664
   directory mask = 0775
   force user = admin
   # Remove or comment out: force group = admin
```

**Option B: Fix force group** (if group should exist):
```bash
# First, ensure the group exists
sudo groupadd admin  # Only if it doesn't exist
getent group admin   # Verify it exists

# Then in smb.conf, keep:
force group = admin
```

**Fix 3: Use User's Actual Primary Group**

Find your user's actual primary group and use that:

```bash
# Find your user's primary group
id -gn admin
# Example output: admin or users or pi

# Edit smb.conf and use the actual group name
sudo nano /etc/samba/smb.conf
```

In `[devdeck]` section, set:
```ini
force group = admin  # or whatever id -gn showed
```

**Fix 4: Remove force group Entirely (Simplest Fix)**

The simplest solution is to remove `force group` and let Samba use the user's default group:

```bash
sudo nano /etc/samba/smb.conf
```

In the `[devdeck]` section, remove or comment out the `force group` line:
```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin
   create mask = 0664
   directory mask = 0775
   force user = admin
   # force group = admin  ← Comment this out or remove it
```

Then restart Samba:
```bash
sudo systemctl restart smbd
```

Test again:
```bash
smbclient //localhost/devdeck -U admin
```

**Most Common Fix**: Fix 4 (remove `force group`) usually resolves this error.

**Solution 9: Temporarily Enable Guest Access (Testing Only)**

To test if it's an authentication issue, temporarily enable guest access:

On Raspberry Pi:
```bash
sudo nano /etc/samba/smb.conf
```

In the `[devdeck]` section, add:
```ini
[devdeck]
   ...
   guest ok = yes
   guest only = yes
```

Then restart:
```bash
sudo systemctl restart smbd
```

Try accessing from Windows without credentials. **If this works**, the issue is authentication format. **Remove the guest access** after testing and use Solution 1-8 instead.

**Most Common Fix**: Solution 1 (username format) or Solution 2 (verify Samba user exists) usually resolves this.

#### Transitioning from Guest Access to Secure Access

**If guest access worked**, the share is configured correctly but authentication needs to be fixed. Follow these steps to enable secure access:

**Step 1: Remove Guest Access**

```bash
# Edit Samba config
sudo nano /etc/samba/smb.conf
```

In the `[devdeck]` section, **remove or comment out** these lines:
```ini
[devdeck]
   ...
   # guest ok = yes      ← Comment this out
   # guest only = yes    ← Comment this out
```

**Step 2: Ensure Secure Configuration**

Make sure your `[devdeck]` section looks like this (secure configuration):

```ini
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin
   create mask = 0664
   directory mask = 0775
   force user = admin
   # force group = admin  ← Remove or comment out if causing issues
```

**Step 3: Verify Samba User Exists**

```bash
# Check if your user exists in Samba
sudo pdbedit -L
# Should show: admin

# If NOT listed, add it:
sudo smbpasswd -a admin
# Enter password twice (this is your Samba password)

# Enable the user:
sudo smbpasswd -e admin

# Verify:
sudo pdbedit -L -v admin
```

**Step 4: Restart Samba**

```bash
sudo systemctl restart smbd
```

**Step 5: Test from Raspberry Pi**

```bash
# Test with authentication
smbclient //localhost/devdeck -U admin
# Enter your Samba password
# Type 'ls' to list files
# Type 'exit' to quit
```

**Step 6: Test from Windows**

Now try from Windows:

1. **Press `Windows Key + R`**
2. **Type**: `\\10.0.0.51\devdeck` (your Pi's IP)
3. **Enter credentials**:
   - Username: `admin` (or try `WORKGROUP\admin` if that doesn't work)
   - Password: Your Samba password (the one you set with `sudo smbpasswd -a admin`)
4. **Click OK**

**If it still doesn't work**, try these username formats in order:
- `admin`
- `WORKGROUP\admin`
- `10.0.0.51\admin` (your Pi's IP)

**Note**: Guest access is convenient but insecure - anyone on your network can access the share. Secure access with authentication is recommended for production use.

**Raspberry Pi-Side Checks:**

```bash
# 1. Check Samba service is running
sudo systemctl status smbd

# 2. Check firewall (if enabled)
sudo ufw status
# If firewall is active, allow Samba:
sudo ufw allow samba

# 3. Verify Samba configuration
sudo testparm -s | grep -A 15 "\[devdeck\]"
# Should show: read only = No (writable), browseable = yes, valid users = admin

# 4. Check Samba logs
sudo tail -f /var/log/samba/log.smbd

# 5. Verify user is enabled in Samba
sudo pdbedit -L
# Should show your user (admin or your username)

# 6. Restart Samba service
sudo systemctl restart smbd
```

#### Can See Folders But Cannot Browse Into devdeck

**Problem**: You can connect and see `admin` and `devdeck` folders, but cannot browse into the `devdeck` folder

**This usually means you're connecting to a parent share instead of the `devdeck` share directly.**

**Solution 1: Connect Directly to the devdeck Share**

Instead of browsing through `\\IP\admin` or similar, connect directly:

1. **Press `Windows Key + R`**
2. **Type**: `\\192.168.1.100\devdeck` (replace with your Pi's IP)
3. **Press Enter**
4. **Enter credentials**:
   - Username: `admin` (your Pi username)
   - Password: Your Samba password
5. You should now see the contents of `~/devdeck` directly

**Solution 2: Verify Samba Share Configuration**

On Raspberry Pi, check that the `devdeck` share is properly configured:

```bash
# Test Samba configuration
sudo testparm -s | grep -A 10 "\[devdeck\]"
```

You should see output like:
```
[devdeck]
   comment = DevDeck Application Directory
   path = /home/admin/devdeck
   browseable = yes
   writeable = yes
   valid users = admin
```

**Solution 3: Check Share Permissions**

```bash
# Verify the devdeck directory exists and has correct permissions
ls -la ~/devdeck

# Fix ownership if needed
sudo chown -R $USER:$USER ~/devdeck

# Fix permissions
find ~/devdeck -type d -exec chmod 755 {} \;
find ~/devdeck -type f -exec chmod 664 {} \;

# Verify Samba can access it
sudo testparm
```

**Solution 4: Check if Multiple Shares Are Configured**

You might have both a home directory share and a devdeck share. Check:

```bash
# List all Samba shares
sudo testparm -s | grep "^\["
```

If you see both `[admin]` (or `[homes]`) and `[devdeck]`, you need to connect to `\\IP\devdeck` specifically, not `\\IP\admin`.

**Solution 5: Restart Samba After Configuration Changes**

```bash
# Restart Samba to apply any changes
sudo systemctl restart smbd

# Verify it's running
sudo systemctl status smbd
```

**Solution 6: Access via Network Browser (Alternative)**

1. Open File Explorer
2. Click "Network" in the left sidebar
3. Find your Raspberry Pi in the list
4. Double-click it
5. You should see the `devdeck` share listed
6. Double-click `devdeck` to access it

#### Authentication Fails

**Problem**: Windows prompts for password but authentication fails

**Solutions**:

```bash
# 1. Verify Samba user exists and is enabled
sudo pdbedit -L -v

# 2. Reset Samba password (replace 'admin' with your username)
sudo smbpasswd -a admin
sudo smbpasswd -e admin

# 3. Check if user exists in system (replace 'admin' with your username)
id admin
whoami  # Find your username

# 4. Verify Samba configuration allows the user
sudo testparm -s | grep -A 5 "\[devdeck\]"
```

#### Permission Denied Errors

**Problem**: Can access share but cannot create/modify files, OR application gets "[Errno 13] Permission denied" errors

**Solutions**:

```bash
# 1. Check directory ownership (replace 'admin' with your username)
ls -la ~/devdeck
whoami  # Verify your username

# 2. Fix ownership if needed (replace 'admin' with your username)
sudo chown -R $USER:$USER ~/devdeck

# 3. Fix directory permissions (directories need execute permission)
find ~/devdeck -type d -exec chmod 755 {} \;

# 4. Fix file permissions (files need read/write for owner - 664, not 644)
find ~/devdeck -type f -exec chmod 664 {} \;

# 5. Make scripts executable
find ~/devdeck -name "*.sh" -exec chmod 755 {} \;

# 6. Verify config files are writable (critical for application)
ls -la ~/devdeck/config/
# Should show: -rw-rw-r-- (664) for files, not -rw-r--r-- (644)

# 7. Verify Samba configuration has writeable = yes
sudo testparm -s | grep -A 5 "\[devdeck\]"

# 8. Check Samba force user matches your username
sudo testparm -s | grep "force user"
# Should show: force user = admin (or your username)
```

**Critical Fix for Application Errors**: If you see `[Errno 13] Permission denied: '/home/admin/devdeck/config/key_mappings.json'`:

```bash
# Fix ownership and permissions for the entire devdeck directory
sudo chown -R $USER:$USER ~/devdeck
find ~/devdeck -type d -exec chmod 755 {} \;
find ~/devdeck -type f -exec chmod 664 {} \;

# Verify config files are writable
chmod 664 ~/devdeck/config/*.json ~/devdeck/config/*.yml

# Restart the application service
sudo systemctl restart devdeck.service
```

**Root Cause**: The `chmod 644` command makes files read-only for the owner. Config files need `664` permissions (read/write for owner) so the application can modify them.

#### Windows Shows "Network Path Not Found"

**Problem**: Windows cannot find the network path

**Solutions**:

```bash
# 1. Verify IP address is correct
hostname -I

# 2. Test connectivity from Windows (PowerShell):
# Test-NetConnection -ComputerName 192.168.1.100 -Port 445

# 3. Check if Samba is listening on port 445
sudo netstat -tlnp | grep 445

# 4. Verify network connectivity
ping raspberry-pi-ip  # From Windows

# 5. Check Windows Firewall (may block SMB)
# Windows: Settings > Network & Internet > Windows Firewall
```

#### Slow File Transfers

**Problem**: File transfers are very slow

**Solutions**:

```bash
# 1. Add performance optimizations to Samba config
sudo nano /etc/samba/smb.conf
```

Add to the `[global]` section (at the top of the file):

```ini
[global]
   socket options = TCP_NODELAY IPTOS_LOWDELAY SO_RCVBUF=131072 SO_SNDBUF=131072
   read raw = yes
   write raw = yes
   max xmit = 65536
   dead time = 15
   getwd cache = yes
```

Then restart Samba:

```bash
sudo systemctl restart smbd
```

### Security Considerations

1. **Use Secure Configuration**: Prefer Option A (password-protected) over guest access
2. **Strong Passwords**: Use a strong Samba password different from your Linux password
3. **Network Isolation**: Only enable Samba on trusted local networks
4. **Firewall**: Consider restricting Samba access to specific IP addresses:
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 445
   ```
5. **Regular Updates**: Keep Samba updated:
   ```bash
   sudo apt update && sudo apt upgrade samba
   ```

### Additional Samba Shares (Optional)

You can add more shares by adding additional sections to `/etc/samba/smb.conf`. For example, to share your entire home directory:

```ini
[home]
   comment = Home Directory
   path = /home/pi
   browseable = yes
   writeable = yes
   valid users = pi
   create mask = 0644
   directory mask = 0755
```

After adding new shares, restart Samba:

```bash
sudo systemctl restart smbd
```

---

## Auto-Start on Boot (Systemd Service)

The recommended way to automatically start the application on boot is using a **systemd service**. This runs the application in the background (not in a terminal), but you can easily control it using systemctl commands.

**Note**: The service runs in the background, so you won't see it in a terminal window. However, you can:
- Start/stop/restart it using `systemctl` commands
- View logs using `journalctl` commands
- Check its status at any time

### Step 1: Create Systemd Service File

**Option A: Use the provided template (Recommended)**

```bash
# Navigate to your project directory
cd ~/devdeck

# Copy the service template
sudo cp scripts/systemd/devdeck.service /etc/systemd/system/devdeck.service

# Edit the service file to match your username and paths
sudo nano /etc/systemd/system/devdeck.service
```

**Option B: Create manually**

```bash
# Create service file
sudo nano /etc/systemd/system/devdeck.service
```

Add the following content (adjust paths as needed):
```ini
[Unit]
Description=Ketron EVM Stream Deck Controller
After=network.target sound.target
Wants=network-online.target

[Service]
Type=simple
# IMPORTANT: Replace 'admin' with your actual username
User=admin
# IMPORTANT: Replace '/home/admin/devdeck' with your actual project path
WorkingDirectory=/home/admin/devdeck
Environment="PATH=/home/admin/devdeck/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/admin/devdeck/venv/bin/python -m devdeck.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Important**: 
- Replace `admin` with your actual username (e.g., `pi`, `admin`, etc.)
- Replace `/home/admin/devdeck` with your actual project directory path
- You can find your username with: `whoami`
- You can find your home directory with: `echo $HOME`

### Step 2: Enable and Start Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable service (this makes it start automatically on boot)
sudo systemctl enable devdeck.service

# Start the service now (don't wait for reboot)
sudo systemctl start devdeck.service

# Check if it's running
sudo systemctl status devdeck.service
```

**Expected output**: You should see `Active: active (running)` in green.

### Step 3: View Service Logs

```bash
# View recent logs
sudo journalctl -u devdeck.service -n 50

# Follow logs in real-time
sudo journalctl -u devdeck.service -f

# View logs since boot
sudo journalctl -u devdeck.service -b
```

### Step 4: Service Management Commands

**Control the service** (the application runs in the background, not in a terminal):

```bash
# Start the service
sudo systemctl start devdeck.service

# Stop the service
sudo systemctl stop devdeck.service

# Restart the service (useful after making code changes)
sudo systemctl restart devdeck.service

# Check if it's running
sudo systemctl status devdeck.service

# Disable auto-start on boot (service will not start automatically)
sudo systemctl disable devdeck.service

# Enable auto-start on boot (service will start automatically on boot)
sudo systemctl enable devdeck.service
```

**Note**: Even though the service runs in the background, you can easily stop it using `sudo systemctl stop devdeck.service` from any terminal.

### Step 5: Auto-Open Terminal with Logs (Optional)

If you want a terminal window to automatically open showing the service logs when you log in to the desktop, you can install an autostart entry:

```bash
cd ~/devdeck
bash scripts/systemd/install-logs-autostart.sh
```

This will:
- Create a desktop autostart entry
- Automatically open a terminal window 5 seconds after login
- Show the devdeck service logs in real-time
- Keep the terminal open so you can see the logs

**To disable the autostart:**
```bash
rm ~/.config/autostart/devdeck-logs.desktop
```

**To re-enable:**
```bash
bash ~/devdeck/scripts/systemd/install-logs-autostart.sh
```

**Note**: This feature requires a desktop environment (Raspberry Pi OS Desktop). It won't work on headless systems.

---

## Alternative: Running in a Terminal Session (Screen/Tmux)

If you prefer to run the application in a terminal session that you can attach to and see the output directly, you can use `screen` or `tmux`. This is useful for debugging or if you want to see the logs in real-time in a terminal.

### Option 1: Using Screen

```bash
# Install screen (if not already installed)
sudo apt install -y screen

# Create a startup script
cat > ~/start-devdeck-screen.sh << 'EOF'
#!/bin/bash
cd ~/devdeck
source venv/bin/activate
python -m devdeck.main
EOF

chmod +x ~/start-devdeck-screen.sh

# Start in a screen session (detached)
screen -dmS devdeck ~/start-devdeck-screen.sh

# Attach to the screen session to see output
screen -r devdeck

# Detach from screen: Press Ctrl+A, then D
# Stop the application: Attach to screen, then press Ctrl+C
```

### Option 2: Using Tmux

```bash
# Install tmux (if not already installed)
sudo apt install -y tmux

# Create a startup script
cat > ~/start-devdeck-tmux.sh << 'EOF'
#!/bin/bash
cd ~/devdeck
source venv/bin/activate
python -m devdeck.main
EOF

chmod +x ~/start-devdeck-tmux.sh

# Start in a tmux session (detached)
tmux new-session -d -s devdeck '~/start-devdeck-tmux.sh'

# Attach to the tmux session to see output
tmux attach-session -t devdeck

# Detach from tmux: Press Ctrl+B, then D
# Stop the application: Attach to tmux, then press Ctrl+C
```

### Option 3: Crontab (Alternative to Systemd)

If you prefer not to use systemd:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
@reboot cd /home/admin/devdeck && /home/admin/devdeck/venv/bin/python -m devdeck.main >> /home/admin/devdeck/logs/devdeck.log 2>&1
```

**Note**: The systemd service method (described above) is recommended because it provides better process management, automatic restarts, and easier log viewing.

---

## Testing and Verification

### Step 1: Verify Hardware Connections

```bash
# Check Stream Deck
lsusb | grep -i elgato

# Check MIDI device
lsusb | grep -i midi
aconnect -l
```

### Step 2: Test MIDI Communication

```bash
# Navigate to project root directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# List MIDI ports (must be run from project root)
python3 tests/list_midi_ports.py

# Test Ketron SysEx
python3 tests/devdeck/ketron/test_ketron_sysex.py "Your MIDI Port Name"
```

### Step 2a: Test MIDI Output (Verify MIDI Traffic Leaves Raspberry Pi)

**Problem**: You want to verify that MIDI messages are actually leaving the Raspberry Pi through the USB MIDI interface.

**Method 1: Use Python Test Script (Recommended)**

```bash
# Navigate to project root directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Run MIDI output test script
python3 scripts/test/test_midi_output.py

# Or specify a port name:
python3 scripts/test/test_midi_output.py "USB MIDI Interface MIDI 1"
```

This script will:
- List all available MIDI ports
- Open the specified port
- Send test MIDI CC, Note, and SysEx messages
- Report success/failure for each message type

**Method 2: Use Command-Line MIDI Tools**

```bash
# Install ALSA MIDI utilities (if not already installed)
sudo apt install -y alsa-utils

# List MIDI ports
amidi -l

# Send a MIDI CC message using amidi
# Format: amidi -p <port> -S <hex bytes>
# Example: Send CC 102, value 64 on channel 0
# CC message format: 0xBn 0x66 0x40 (B=channel 0, 66=CC 102, 40=value 64)
amidi -p hw:1,0,0 -S "B0 66 40"

# Send a Note On message
# Format: 0x9n <note> <velocity> (9=Note On, n=channel)
# Example: Note C4 (60) with velocity 100 on channel 0
amidi -p hw:1,0,0 -S "90 3C 64"

# Send Note Off
amidi -p hw:1,0,0 -S "80 3C 00"
```

**Method 3: Monitor MIDI Traffic with aseqdump**

```bash
# Install ALSA sequencer utilities
sudo apt install -y alsa-utils

# Monitor all MIDI traffic on a specific port
# First, find your port name:
aconnect -l

# Then monitor it (replace with your actual port/client number):
aseqdump -p 20:0

# Or monitor all MIDI traffic:
aseqdump -l
```

**Method 3a: Use aconnect to Route MIDI for Testing**

The `aconnect` tool can be used to route MIDI between ports, which is useful for testing and verification. This technique is based on [using a Raspberry Pi as a MIDI USB/5-pin bridge](https://m635j520.blogspot.com/2017/01/using-raspberry-pi-as-midi-usb5-pin.html).

**Step 1: List All MIDI Ports**

```bash
# List all MIDI input and output ports
aconnect -l

# Or list only input ports:
aconnect -i

# Or list only output ports:
aconnect -o
```

**Example Output**:
```
client 0: 'System' [type=kernel]
    0 'Timer           '
    1 'Announce        '
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
client 20: 'USB MIDI Interface' [type=kernel,card=1]
    0 'USB MIDI Interface MIDI 1'
client 24: 'EVM Stream Deck Controller' [type=user,pid=1230]
    0 'output          '
```

**Step 2: Connect MIDI Ports for Testing**

You can use `aconnect` to route MIDI from your application's virtual port to your USB MIDI interface:

**First, identify the correct port numbers:**

```bash
# List all MIDI ports with their client:port numbers
aconnect -l

# Or list only output ports (sources):
aconnect -o

# Or list only input ports (destinations):
aconnect -i
```

**Then connect the ports:**

```bash
# Syntax: aconnect <source_client>:<source_port> <dest_client>:<dest_port>
# Connect virtual port (client 24, port 0) to USB MIDI interface (client 20, port 0)
aconnect 24:0 20:0

# Verify the connection:
aconnect -l
# Should show: "Connecting To: 20:0" under client 24
```

**Common Issues and Solutions:**

1. **"client 24:0 is not available" or "client 20:0 is not available"**:
   - The port numbers don't exist or have changed
   - Run `aconnect -l` again to get current port numbers
   - Port numbers can change when devices are reconnected

2. **"client 24:0 is not a valid source"**:
   - The source port must be an output port
   - Check with `aconnect -o` to see available output ports
   - Virtual ports created by applications are usually output ports

3. **"client 20:0 is not a valid destination"**:
   - The destination port must be an input port
   - Check with `aconnect -i` to see available input ports
   - USB MIDI interfaces usually have both input and output ports

4. **"Connection failed: Device or resource busy"**:
   - The port is already connected to another port
   - Disconnect existing connections first: `aconnect -x 24:0`
   - Or disconnect specific connection: `aconnect -d 24:0 20:0`

5. **"Permission denied"**:
   - User needs to be in the `audio` group
   - Add user: `sudo usermod -a -G audio $USER`
   - Log out and log back in for changes to take effect

**Example Workflow:**

```bash
# Step 1: Start your application (creates virtual MIDI port)
cd ~/devdeck
source venv/bin/activate
python3 -m devdeck.main &
# Note the PID or check aconnect -l in another terminal

# Step 2: In another terminal, find the port numbers
aconnect -l
# Look for "EVM Stream Deck Controller" or similar - note the client number
# Look for your USB MIDI interface - note its client number

# Step 3: Connect them (replace with actual numbers from step 2)
aconnect 24:0 20:0

# Step 4: Verify connection
aconnect -l
# Should show connection between the ports

# Step 5: Monitor MIDI traffic
aseqdump -p 20:0
```

**Step 3: Test MIDI Routing**

1. **Start your application** (creates virtual MIDI port)
2. **Connect the virtual port to USB MIDI interface**:
   ```bash
   aconnect -l  # Find your virtual port number
   aconnect 24:0 20:0  # Connect virtual port to USB MIDI interface
   ```
3. **Monitor MIDI traffic** on the USB MIDI interface:
   ```bash
   aseqdump -p 20:0
   ```
4. **Press buttons on Stream Deck** - you should see MIDI messages in aseqdump

**Step 4: Disconnect When Done**

```bash
# Disconnect ports
aconnect -d 24:0 20:0

# Or disconnect all connections from a port:
aconnect -x 24:0
```

**Use Cases**:
- Route MIDI from virtual port to hardware MIDI interface
- Connect multiple MIDI devices together
- Create MIDI bridges between USB and 5-pin MIDI devices
- Test MIDI routing without modifying application code

**Note**: Connections made with `aconnect` are temporary and will be lost on reboot. For permanent routing, see the article on [automatic MIDI connection setup](https://m635j520.blogspot.com/2017/01/using-raspberry-pi-as-midi-usb5-pin.html).

**Method 4: Test with MIDI Monitor on Another Device**

1. **Connect USB MIDI Interface to Windows Computer**:
   - Connect the USB MIDI interface to your Windows laptop
   - Open MidiView or another MIDI monitor
   - The interface should appear in MidiView

2. **On Raspberry Pi, Send Test Messages**:
   ```bash
   cd ~/devdeck
   source venv/bin/activate
   python3 scripts/test/test_midi_output.py "USB MIDI Interface MIDI 1"
   ```

3. **Watch MidiView on Windows**:
   - You should see MIDI messages appearing in real-time
   - If messages appear, MIDI is successfully leaving the Raspberry Pi

**Method 5: Test with Physical MIDI Device**

1. **Connect MIDI Device to USB MIDI Interface**:
   - Connect MIDI device's MIDI IN to USB MIDI interface's MIDI OUT
   - Power on the MIDI device

2. **Send Test Messages from Raspberry Pi**:
   ```bash
   cd ~/devdeck
   source venv/bin/activate
   python3 scripts/test/test_midi_output.py "USB MIDI Interface MIDI 1"
   ```

3. **Check if Device Responds**:
   - If the device has LEDs or displays, check if they respond
   - If it's a synthesizer, check if notes play
   - If it's a controller, check if it receives the commands

**Method 6: Use aplaymidi (Play MIDI File)**

```bash
# Create a simple MIDI test file or download one
# Then play it through the MIDI interface:
aplaymidi -p hw:1,0,0 test.mid

# Or use a MIDI file from the system:
# (if available)
```

**Troubleshooting: No MIDI Traffic Detected**

If MIDI messages aren't leaving the Raspberry Pi:

1. **Verify USB MIDI Interface is Detected**:
   ```bash
   lsusb | grep -i midi
   aconnect -l
   amidi -l
   ```

2. **Check Port Name is Correct**:
   ```bash
   # List all ports
   python3 tests/list_midi_ports.py
   
   # Use the exact port name (case-sensitive)
   python3 scripts/test/test_midi_output.py "Exact Port Name"
   ```

3. **Check Permissions**:
   ```bash
   # Ensure user is in audio group
   groups | grep audio
   
   # If not, add user:
   sudo usermod -a -G audio $USER
   # Then log out and log back in
   ```

4. **Test Port Opening**:
   ```bash
   cd ~/devdeck
   source venv/bin/activate
   python3 -c "
   from devdeck.midi import MidiManager
   m = MidiManager()
   ports = m.list_output_ports()
   print('Available ports:', ports)
   if ports:
       print(f'Opening port: {ports[0]}')
       if m.open_port(ports[0]):
           print('Port opened successfully!')
           m.close_port(ports[0])
       else:
           print('Failed to open port')
   "
   ```

5. **Check for Errors in Logs**:
   ```bash
   # If running as service:
   sudo journalctl -u devdeck.service -f
   
   # Or check system logs:
   dmesg | grep -i midi
   ```

**Expected Results**:

- ✅ **Success**: Test script reports all messages sent successfully, and MIDI monitor shows traffic
- ❌ **Failure**: Test script reports errors, or no MIDI traffic appears in monitor

**Quick Test Command**:

```bash
# Quick one-liner test:
cd ~/devdeck && source venv/bin/activate && python3 scripts/test/test_midi_output.py
```

### Step 3: Test Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run application manually
python3 -m devdeck.main

# Press a few keys on Stream Deck
# Check if Ketron responds
```

### Step 4: Verify Service Operation

```bash
# Check service status
sudo systemctl status devdeck.service

# Check logs for errors
sudo journalctl -u devdeck.service -n 100

# Test key presses
# Verify MIDI messages are sent
```

---

## Troubleshooting

### Stream Deck Not Detected / ProbeError

**Problem**: `ProbeError: Probe failed to find any functional HID backend` or `No suitable LibUSB HIDAPI library found`

**Solutions**:
```bash
# Install required HIDAPI libraries
sudo apt update
sudo apt install -y libhidapi-libusb0 libhidapi-dev libusb-1.0-0-dev

# Verify libraries are installed
ldconfig -p | grep hidapi

# If libraries are installed but still not found, try:
sudo ldconfig

# Reinstall Python streamdeck package
source venv/bin/activate
pip install --force-reinstall streamdeck

# Check USB connection
lsusb | grep -i elgato

# Verify udev rules
cat /etc/udev/rules.d/50-streamdeck.rules

# Check user groups
groups $USER

# Test USB permissions
sudo chmod 666 /dev/bus/usb/*/*

# Restart udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reboot if necessary
sudo reboot
```

**Note**: The `libhidapi-libusb0` package provides the `libhidapi-libusb.so` library that the Stream Deck Python library requires. This is a runtime dependency that must be installed at the system level.

### Could Not Open HID Device

**Problem**: `TransportError: Could not open HID device.` - The library can find the device but cannot open it due to permissions.

**Solutions**:
```bash
# Step 1: Verify Stream Deck is connected
lsusb | grep -i elgato
# Should show something like: Bus 001 Device 003: ID 0fd9:0060 Elgato Systems GmbH

# Step 2: Check if udev rules file exists
ls -la /etc/udev/rules.d/50-streamdeck.rules

# Step 3: If file doesn't exist, create it (see USB Permissions Configuration section above)
sudo nano /etc/udev/rules.d/50-streamdeck.rules
# Add the udev rules for your Stream Deck model

# Step 4: Verify your user is in the plugdev group
groups $USER
# Should include 'plugdev' in the output

# Step 5: If not in plugdev group, add yourself
sudo usermod -a -G plugdev $USER

# Step 6: Apply group changes (choose one method):
# Option A: Log out and log back in (recommended)
# Option B: Use newgrp (temporary, for current session)
newgrp plugdev

# Step 7: Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Step 8: Unplug and replug Stream Deck USB cable
# This ensures the new permissions are applied

# Step 9: Verify permissions on USB device
# Find the device path
ls -la /dev/bus/usb/*/* | grep -i elgato
# Or check all USB devices
ls -la /dev/bus/usb/*/*

# Step 10: Test again
cd ~/devdeck
source venv/bin/activate
python3 -m devdeck.main
```

**Important Notes**:
- After adding yourself to the `plugdev` group, you **must log out and log back in** for the change to take effect (or use `newgrp plugdev` for the current session)
- The udev rules must match your Stream Deck model's vendor/product IDs (check with `lsusb`)
- After creating/modifying udev rules, you must unplug and replug the Stream Deck for the rules to apply
- If still having issues, try running with `sudo` temporarily to verify it's a permissions issue:
  ```bash
  sudo -E env "PATH=$PATH" python3 -m devdeck.main
  ```
  (If this works, it confirms a permissions issue - don't run as root permanently)

### MIDI Port Not Found / Ketron EVM Not Detected

**Problem**: Ketron EVM connected via USB but not appearing in MIDI port list

**Symptoms**:
- `lsusb` shows no Ketron device
- `aconnect -l` shows no Ketron MIDI client
- `amidi -l` shows no MIDI devices
- Only "Midi Through" port appears in `python3 tests/list_midi_ports.py`

**Diagnostic Steps**:

1. **Check USB Connection**:
```bash
# Check if device appears in USB listing
lsusb

# Check detailed USB information
lsusb -v | grep -i "ketron\|midi\|audio" -A 5 -B 5

# Monitor USB connections in real-time
sudo dmesg -w
# Then unplug and replug the Ketron EVM - watch for connection messages
```

2. **Check USB MIDI Driver**:
```bash
# Check if USB MIDI driver is loaded
lsmod | grep snd_usb

# If not loaded, load it
sudo modprobe snd-usb-audio

# Make it persistent
echo "snd-usb-audio" | sudo tee -a /etc/modules

# Check dmesg for driver messages
dmesg | grep -i "midi\|usb\|audio" | tail -20
```

3. **Check ALSA Sound Cards**:
```bash
# Check if device appears as sound card
cat /proc/asound/cards

# Check ALSA MIDI ports
aconnect -l
amidi -l

# Restart ALSA if needed
sudo alsa force-reload
```

4. **Check Device Permissions**:
```bash
# Check USB device permissions
ls -la /dev/bus/usb/*/* | grep -i ketron

# Check if user is in audio group (required for MIDI)
groups | grep audio

# If not in audio group, add user:
sudo usermod -a -G audio $USER
# Then log out and log back in
```

**Common Solutions**:

1. **USB MIDI Driver Not Loaded**:
   - Load the driver: `sudo modprobe snd-usb-audio`
   - Make it persistent: `echo "snd-usb-audio" | sudo tee -a /etc/modules`

2. **Device Not in USB MIDI Mode**:
   - Some devices have multiple USB modes (storage, MIDI, etc.)
   - Check Ketron EVM settings/menu for USB mode selection
   - Try unplugging and replugging the USB cable
   - Power cycle the Ketron EVM

3. **Device Not Recognized**:
   - Try different USB cable
   - Try different USB port on Raspberry Pi
   - Check if device works on Windows to verify USB functionality

4. **ALSA Not Recognizing Device**:
   - Restart ALSA: `sudo alsa force-reload`
   - Restart audio system: `sudo systemctl restart alsa-state`
   - Check kernel messages: `dmesg | tail -30`

5. **Using Virtual MIDI Port Instead**:
   - If hardware device cannot be detected, the application will create a virtual MIDI port
   - You'll need to use MIDI routing software (like `aconnect` or `qjackctl`) to connect the virtual port to the hardware device
   - Or configure the application to use a specific hardware port name if it becomes available

**Important Discovery: Ketron EVM Uses Non-Standard USB MIDI Protocol**

Based on testing, the Ketron EVM does **not** use standard USB MIDI protocol that Linux/Windows recognizes. Instead:

- ✅ **Works with CircuitPython's `usb_midi` library** (firmware-level implementation on RP2040/MacroPad)
- ❌ **Does NOT work as standard USB MIDI device** (won't appear in `lsusb`, `aconnect -l`, or `amidi -l`)
- ❌ **Does NOT work on Windows** (even with standard MIDI drivers)
- ❌ **No USB mode setting** (device doesn't have configurable USB modes)

**Why This Happens**:
- The Ketron EVM uses a proprietary or non-standard USB MIDI protocol
- CircuitPython's `usb_midi` implements USB MIDI at the firmware level, not as a standard OS device
- Standard Linux/Windows USB MIDI drivers cannot recognize this protocol
- The device will never appear in standard MIDI port listings

**Solutions**:

**Solution 1: Use MacroPad as MIDI Bridge (Recommended)**

If you have an Adafruit MacroPad (or other CircuitPython device) that can communicate with the Ketron EVM:

1. **Connect MacroPad to Raspberry Pi via USB**:
   - The MacroPad should appear as a standard USB MIDI device
   - Check with: `lsusb`, `aconnect -l`, `python3 tests/list_midi_ports.py`

2. **Configure Application to Use MacroPad Port**:
   - The MacroPad will forward MIDI messages to the Ketron EVM
   - Add the MacroPad's MIDI port name to `settings.yml`:
     ```yaml
     settings:
       port: "MacroPad MIDI 1"  # Or whatever port name appears
     ```

3. **Verify MacroPad Detection**:
   ```bash
   # With MacroPad connected to Raspberry Pi
   lsusb | grep -i "adafruit\|rp2040\|circuitpython"
   aconnect -l
   python3 tests/list_midi_ports.py
   ```

**Solution 2: Use USB MIDI Interface**

If you have a standard USB MIDI interface (e.g., Roland UM-ONE, M-Audio Uno):

1. **Connect Ketron EVM to Interface via 5-Pin MIDI Cables**:
   - Use traditional MIDI DIN cables (5-pin)
   - Connect Ketron EVM MIDI OUT to Interface MIDI IN

2. **Connect Interface to Raspberry Pi via USB**:
   - The interface should appear as a standard USB MIDI device
   - Check with: `lsusb`, `aconnect -l`, `python3 tests/list_midi_ports.py`

3. **Configure Application to Use Interface Port**:
   - Add the interface's MIDI port name to `settings.yml`

**Solution 3: Network MIDI (If Supported)**

Some devices support network MIDI. Check if the Ketron EVM has network MIDI capabilities:
- Requires network MIDI software on Raspberry Pi
- More complex setup, not recommended unless necessary

**Solution 4: Use Virtual MIDI Port with Routing**

If no hardware bridge is available:

1. **Application Creates Virtual MIDI Port**:
   - The application will create "EVM Stream Deck Controller" virtual port
   - This port appears in `aconnect -l` and `python3 tests/list_midi_ports.py`

2. **Use MIDI Routing Software**:
   - Install `qjackctl` or similar MIDI routing tool
   - Connect virtual port to hardware device (if available)
   - Or use `aconnect` to route MIDI between ports

**Testing MacroPad as Bridge**:

```bash
# Connect MacroPad to Raspberry Pi
# Then check if it appears:

lsusb | grep -i "adafruit\|rp2040"
aconnect -l
python3 tests/list_midi_ports.py

# If MacroPad appears, note the port name and add it to settings.yml
```

**Note**: The Ketron EVM's USB MIDI protocol is proprietary and only works with CircuitPython's firmware-level USB MIDI implementation. Standard OS-level USB MIDI drivers cannot communicate with it directly.

### MIDI Port Not Found (Generic)

**Problem**: MIDI device not detected

**Solutions**:
```bash
# List MIDI devices
aconnect -l
amidi -l

# Check USB MIDI connection
lsusb | grep -i midi

# Test ALSA MIDI
aplaymidi -l

# Check ALSA configuration
cat /proc/asound/cards
```

### Using aseqdump for USB MIDI Troubleshooting

**Tool**: `aseqdump` - A command-line tool for monitoring MIDI events (part of the `alsa-utils` package)

This tool is useful for debugging USB MIDI connections and verifying that MIDI messages are being sent correctly.

**Step 1: Install alsa-utils (if not already installed)**

```bash
# Install alsa-utils package (includes aseqdump)
sudo apt install -y alsa-utils
```

**Step 2: List Available MIDI Ports**

```bash
# List all MIDI clients and ports
aseqdump -l
```

This will show a list of clients and ports, including any connected USB MIDI devices. The output will look something like:
```
 Port    Client name                      Port name
  0:0    System                          Timer
  0:1    System                          Announce
 20:0    Launchkey 25                    Launchkey 25 MIDI 1
```

**Step 3: Monitor MIDI Events from a Specific Port**

```bash
# Dump MIDI events from a specific port
aseqdump -p client:port
```

Replace `client:port` with the identified client and port number of your MIDI output device from the previous step. For example:
```bash
# Monitor Launchkey 25 MIDI 1 (client 20, port 0)
aseqdump -p 20:0
```

This will display MIDI messages in real-time as they are sent, showing the message type, channel, and data. Press `Ctrl+C` to stop monitoring.

**Example Output**:
```
Waiting for data. Press Ctrl+C to end.
Source  Event                  Ch  Data
 20:0   Control Change          0, controller 102, value 64
 20:0   Note on                 0, note 60, velocity 100
 20:0   Note off                0, note 60, velocity 0
```

**Use Cases**:
- Verify that MIDI devices are detected by ALSA
- Monitor MIDI messages being sent from your application
- Debug MIDI communication issues
- Identify the correct client:port numbers for your MIDI devices

**Note**: The `aseqdump` tool works with ALSA MIDI ports. If your MIDI device appears in `aseqdump -l`, it should also be available to your application through the `mido` library.

### Testing MIDI Output with mido

**Tool**: Direct Python test using the `mido` library

This test allows you to verify that MIDI output ports are accessible and can send messages correctly. This is useful when troubleshooting MIDI communication issues.

**Step 1: Activate Virtual Environment**

```bash
# Navigate to project root
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate
```

**Step 2: List Available MIDI Output Ports**

```bash
# Run Python to list output ports
python3 -c "import mido; print('Available MIDI output ports:'); [print(f'  - {port}') for port in mido.get_output_names()]"
```

This will display all available MIDI output ports. Note the exact name of your MIDI device.

**Step 3: Test MIDI Output**

Create a test script or run directly in Python:

```bash
# Test MIDI output (replace 'Your MIDI Output Port Name' with actual port name)
python3 << 'EOF'
import mido

# List output ports
print("Available MIDI output ports:")
for port in mido.get_output_names():
    print(f"  - {port}")

# Open the output port you are sending messages to
# Replace 'Your MIDI Output Port Name' with the actual name
port_name = 'Your MIDI Output Port Name'  # Change this to your MIDI port name
try:
    outport = mido.open_output(port_name)
    print(f"\n✓ Successfully opened MIDI output port: {port_name}")
    
    # Example: Send a note on message
    outport.send(mido.Message('note_on', note=60, velocity=64))
    print("✓ Sent note_on message (note=60, velocity=64)")
    
    # Send note off after a short delay
    import time
    time.sleep(0.1)
    outport.send(mido.Message('note_off', note=60, velocity=0))
    print("✓ Sent note_off message")
    
    # Close the port
    outport.close()
    print("✓ MIDI port closed successfully")
except Exception as e:
    print(f"\n✗ Error: {e}")
EOF
```

**Alternative: Interactive Test Script**

You can also create a reusable test script:

```bash
# Create test script
cat > ~/devdeck/test_midi_output.py << 'EOF'
#!/usr/bin/env python3
import mido
import sys

# List output ports
print("Available MIDI output ports:")
ports = mido.get_output_names()
if not ports:
    print("  No MIDI output ports found!")
    sys.exit(1)

for i, port in enumerate(ports):
    print(f"  {i}: {port}")

# If port name provided as argument, use it; otherwise use first port
if len(sys.argv) > 1:
    port_name = sys.argv[1]
else:
    port_name = ports[0]
    print(f"\nUsing first available port: {port_name}")

try:
    # Open the output port
    outport = mido.open_output(port_name)
    print(f"\n✓ Successfully opened MIDI output port: {port_name}")
    
    # Send a test note on message
    outport.send(mido.Message('note_on', note=60, velocity=64))
    print("✓ Sent note_on message (note=60, velocity=64)")
    
    # Wait a moment
    import time
    time.sleep(0.1)
    
    # Send note off
    outport.send(mido.Message('note_off', note=60, velocity=0))
    print("✓ Sent note_off message")
    
    # Close the port
    outport.close()
    print("✓ MIDI port closed successfully")
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
EOF

# Make script executable
chmod +x ~/devdeck/test_midi_output.py

# Run the test script
python3 ~/devdeck/test_midi_output.py

# Or specify a port name
python3 ~/devdeck/test_midi_output.py "Your MIDI Output Port Name"
```

**Use Cases**:
- Verify that MIDI output ports are accessible
- Test MIDI message sending functionality
- Debug MIDI port connection issues
- Verify that your MIDI device receives messages correctly

**Note**: If you have a MIDI loopback or monitor device, you can also open an input port and listen for echoed messages to verify the complete MIDI path.

### Application Crashes on Startup

**Problem**: Service fails to start

**Solutions**:
```bash
# Check service logs
sudo journalctl -u devdeck.service -n 100

# Check Python errors
cd ~/devdeck
source venv/bin/activate
python3 -m devdeck.main

# Verify dependencies
pip list | grep -E "mido|python-rtmidi|devdeck-core"

# Check configuration files
python3 -c "import yaml; yaml.safe_load(open('config/settings.yml'))"
python3 -c "import json; json.load(open('config/key_mappings.json'))"
```

### Permission Denied Errors

**Problem**: Permission errors accessing USB or files

**Solutions**:
```bash
# Check file permissions
ls -la ~/devdeck

# Fix ownership if needed
sudo chown -R $USER:$USER ~/devdeck

# Verify user groups
groups $USER

# Add to plugdev group if not already
sudo usermod -a -G plugdev $USER
newgrp plugdev
```

### Script Import Errors

**Problem**: `ModuleNotFoundError: No module named 'devdeck'` when running scripts

**Solutions**:
```bash
# Ensure you're in the project root directory
cd ~/devdeck

# Verify you're in the right place (should see devdeck/ directory)
ls -la

# Activate virtual environment
source venv/bin/activate

# Verify Python can find the module
python3 -c "import sys; sys.path.insert(0, '.'); from devdeck.midi import MidiManager; print('✓ Module import OK')"

# Now run scripts from project root
python3 tests/list_midi_ports.py
```

**Important**: All scripts must be run from the project root directory (`~/devdeck`) with the virtual environment activated. The scripts add the project root to Python's path, but they assume you're running from that directory.

### StreamDeck Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'streamdeck'` or `ModuleNotFoundError: No module named 'StreamDeck'`

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify activation (should show venv path)
which python3

# Reinstall dependencies
pip install -r requirements.txt

# Install streamdeck specifically
pip install streamdeck

# Verify installation
pip list | grep streamdeck

# Test with correct import syntax
python3 -c "from StreamDeck.DeviceManager import DeviceManager; print('✓ StreamDeck OK')"

# If still failing, install system USB libraries
sudo apt install -y libusb-1.0-0-dev libhidapi-libusb0 libhidapi-dev
sudo ldconfig
pip install --force-reinstall streamdeck
```

**Note**: The package name is `streamdeck` (lowercase) but you import it as `StreamDeck` (capitalized). Always use `from StreamDeck.DeviceManager import DeviceManager`, not `from streamdeck import StreamDeck`.

### Text Not Showing on Buttons / textsize() Error

**Problem**: Button colors display correctly, but text labels are not visible. Error in logs: `'ImageDraw' object has no attribute 'textsize'`

**Root Cause**: The `devdeck-core` package uses the deprecated `textsize()` method which was removed in Pillow 10.0.0+.

**⚠️ Important: Platform Differences**

This issue affects both Windows and Raspberry Pi, but the fix must be applied separately in each environment's virtual environment. The fix cannot be committed to your project because it's in an external dependency (`devdeck-core`) installed in `venv/`, which is gitignored.

**Recommended Solution: Pin Pillow Version (Prevents Issue)**

The best approach is to pin Pillow to a version before 10.0.0 in `requirements.txt`:

```txt
pillow<10.0.0
```

This ensures both Windows and Raspberry Pi use a compatible Pillow version. After updating `requirements.txt`:
- **Windows**: `pip install -r requirements.txt` (will downgrade if needed)
- **Raspberry Pi**: `pip install -r requirements.txt` (will install compatible version)

**Manual Fix: Apply to devdeck-core (If Pillow 10.0.0+ Already Installed)**

If Pillow 10.0.0+ is already installed, you can manually fix `devdeck-core` in each environment:

**Solutions**:

**Step 1: Check Pillow Version**
```bash
source venv/bin/activate
pip show pillow
# If version is 10.0.0 or higher, you need to fix devdeck-core
```

**Step 2: Fix devdeck-core text_renderer.py**

**On Raspberry Pi:**
```bash
# Find the text_renderer.py file in devdeck-core
find ~/devdeck/venv -name "text_renderer.py" -path "*/devdeck_core/*"

# The file should be at:
# ~/devdeck/venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py

# Edit the file
nano ~/devdeck/venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py
```

**On Windows:**
```powershell
# Find the file
Get-ChildItem -Path "venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py"

# Edit with notepad or your preferred editor
notepad venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py
# Or with VS Code:
code venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py
```

**Step 3: Replace textsize() with textbbox()**

Find this line (around line 258):
```python
label_w, label_h = draw.textsize('%s' % self.text, font=font)
```

Replace it with:
```python
# textsize() was deprecated and removed in Pillow 10.0.0, use textbbox() instead
bbox = draw.textbbox((0, 0), '%s' % self.text, font=font)
label_w = bbox[2] - bbox[0]  # right - left
label_h = bbox[3] - bbox[1]  # bottom - top
```

**Step 4: Save and Restart**
```bash
# Save the file (Ctrl+O, Enter, Ctrl+X in nano)
# Restart the application
python3 -m devdeck.main
```

**Alternative: Downgrade Pillow (Not Recommended)**
```bash
# Only if you can't edit devdeck-core
source venv/bin/activate
pip install "pillow<10.0.0"
```

**⚠️ Critical Troubleshooting Tip: Platform Differences**

**Important Notes**:
- ⚠️ **This fix must be applied separately in each virtual environment** (Windows and Raspberry Pi have separate venvs)
- The fix is applied to your local virtual environment only - it **cannot be committed to git** (venv/ is gitignored)
- If you recreate the venv or reinstall `devdeck-core`, you'll need to reapply this fix
- **Best Practice**: Pin Pillow version in `requirements.txt` (`pillow<10.0.0`) to prevent this issue in new environments
- Consider submitting a patch to the `devdeck-core` project for a permanent upstream solution

**Why This Happens**:
- `devdeck-core` is an external dependency installed in `venv/`
- Each platform (Windows/Raspberry Pi) has its own virtual environment
- The fix must be applied to each environment independently
- Pinning Pillow version in `requirements.txt` ensures consistency across platforms

**Common Causes**:
- Pillow 10.0.0+ installed (textsize() method removed)
- devdeck-core package not updated for Pillow 10.0.0+
- Missing system fonts (DejaVu, Liberation, or Arial)
- Font path issues in devdeck-core library

### Button Actions Not Triggering

**Problem**: Buttons display correctly but pressing them doesn't trigger actions (MIDI messages not sent, commands not executed).

**Solutions**:
```bash
# Step 1: Check if button events are being received
# Look for log messages when pressing buttons
tail -f ~/devdeck/devdeck.log | grep -i "pressed\|key"

# Step 2: Verify MIDI port is open (for MIDI actions)
cd ~/devdeck
source venv/bin/activate
python3 -c "
from devdeck.midi import MidiManager
m = MidiManager()
print('Open ports:', list(m._output_ports.keys()))
print('Available ports:', m.list_output_ports())
"

# Step 3: Check MIDI port permissions
# ALSA MIDI ports may require user to be in 'audio' group
groups $USER
# Should include 'audio' if using ALSA MIDI

# If not in audio group:
sudo usermod -a -G audio $USER
# Log out and log back in for this to take effect

# Step 4: Test MIDI port access directly
python3 -c "
from devdeck.midi import MidiManager
m = MidiManager()
ports = m.list_output_ports()
if ports:
    print(f'Opening port: {ports[0]}')
    if m.open_port(ports[0]):
        print('Port opened successfully')
        if m.send_cc(102, 64, 0, ports[0]):
            print('MIDI message sent successfully')
        else:
            print('Failed to send MIDI message')
    else:
        print('Failed to open port')
else:
    print('No MIDI ports available')
"

# Step 5: Check for MIDI port access errors in logs
tail -f ~/devdeck/devdeck.log | grep -i "midi\|port\|error\|permission"

# Step 6: Verify key_mappings.json is being loaded
cat ~/devdeck/config/key_mappings.json | python3 -m json.tool | head -20

# Step 7: Check if controls are being initialized
# Look for initialization messages in logs
grep -i "initialize\|ketron\|mapping" ~/devdeck/devdeck.log | tail -20
```

**Common Causes**:
- MIDI port not opened (check logs for "Failed to open MIDI port")
- User not in 'audio' group (required for ALSA MIDI on Linux)
- MIDI port permissions issue
- Key mappings not loaded correctly
- Button event callbacks not registered

**Debugging Tips**:
- Enable debug logging by checking log level in main.py
- Press buttons and watch logs in real-time: `tail -f ~/devdeck/devdeck.log`
- Verify MIDI device is connected: `aconnect -l` and `amidi -l`

### MIDI Messages Not Sending

**Problem**: Keys pressed but Ketron doesn't respond

**Solutions**:
```bash
# Navigate to project root
cd ~/devdeck
source venv/bin/activate

# Verify MIDI port name (must be run from project root)
python3 tests/list_midi_ports.py

# Test MIDI directly
python3 tests/devdeck/ketron/test_ketron_sysex.py "Port Name"

# Check if port is open
python3 -c "from devdeck.midi import MidiManager; m = MidiManager(); print(m.list_output_ports())"

# Check application logs
sudo journalctl -u devdeck.service -f
```

### Service Won't Start

**Problem**: systemd service fails to start

**Solutions**:
```bash
# Check service status
sudo systemctl status devdeck.service

# Check service file syntax
sudo systemd-analyze verify devdeck.service

# Check file paths in service file
# Ensure all paths are correct and exist

# Test manual execution
cd ~/devdeck
source venv/bin/activate
python3 -m devdeck.main
```

### High CPU Usage

**Problem**: Application uses too much CPU

**Solutions**:
```bash
# Check CPU usage
top -p $(pgrep -f "devdeck.main")

# Check for errors in logs
sudo journalctl -u devdeck.service | grep -i error

# Verify Stream Deck connection
# Disconnected Stream Deck can cause high CPU
```

### Memory Issues

**Problem**: Application uses too much memory

**Solutions**:
```bash
# Check memory usage
free -h
ps aux | grep devdeck

# Monitor memory over time
watch -n 1 free -h

# Check for memory leaks in logs
sudo journalctl -u devdeck.service | grep -i memory
```

---

## Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Python packages (in virtual environment)
cd ~/devdeck
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart devdeck.service
```

### Backup Configuration

```bash
# Backup configuration files
cp ~/devdeck/config/settings.yml ~/devdeck/config/settings.yml.backup
cp ~/devdeck/config/key_mappings.json ~/devdeck/config/key_mappings.json.backup

# Create full backup
tar -czf ~/devdeck-backup-$(date +%Y%m%d).tar.gz ~/devdeck
```

### Log Rotation

Systemd automatically manages logs, but you can configure log retention:

```bash
# Edit journald config
sudo nano /etc/systemd/journald.conf

# Set MaxRetentionSec (e.g., 1 month)
MaxRetentionSec=1month

# Restart journald
sudo systemctl restart systemd-journald
```

### Monitoring

```bash
# Create monitoring script
nano ~/monitor_devdeck.sh
```

Add:
```bash
#!/bin/bash
if ! systemctl is-active --quiet devdeck.service; then
    echo "DevDeck service is not running!"
    sudo systemctl restart devdeck.service
fi
```

Make executable:
```bash
chmod +x ~/monitor_devdeck.sh
```

Add to crontab (check every 5 minutes):
```bash
crontab -e
# Add: */5 * * * * ~/monitor_devdeck.sh
```

---

## Performance Optimization

### Disable Unnecessary Services

```bash
# Disable Bluetooth if not needed
sudo systemctl disable bluetooth.service

# Disable Wi-Fi if using Ethernet
# (Edit /boot/config.txt or use raspi-config)
```

### Overclock (Optional)

```bash
# Edit boot config
sudo nano /boot/config.txt

# Add (for Pi 5, be cautious):
# over_voltage=2
# arm_freq=2400

# Reboot
sudo reboot
```

### Use High-Quality MicroSD Card

- Use Class 10 or better
- Consider using USB SSD for better performance
- Enable TRIM if using SSD

---

## Security Considerations

### Firewall Configuration

```bash
# Install UFW if not present
sudo apt install ufw

# Allow SSH (if remote access)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Regular Security Updates

```bash
# Set up automatic security updates
sudo apt install unattended-upgrades

# Configure
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Service User Isolation

The systemd service runs as a specific user (not root), which is good for security. Consider creating a dedicated user:

```bash
# Create dedicated user
sudo useradd -r -s /bin/false devdeck

# Update service file to use this user
# Change User=pi to User=devdeck
```

---

## Development on Raspberry Pi 5

### Cursor IDE Compatibility

**Important**: Cursor IDE does not currently run reliably on Raspberry Pi 5.

#### Current Status

- Cursor AppImage crashes on Raspberry Pi 5 (64-bit Raspberry Pi OS)
- Issues are related to hardware acceleration requirements
- No official fix available as of this writing
- **Recommendation**: Do not attempt to run Cursor on Raspberry Pi 5

#### Development Workflow Recommendation

For this project, the recommended workflow is:

1. **Develop on your main computer** (Windows, macOS, or Linux x86_64)
   - Use Cursor IDE on your development machine
   - Edit code, test locally, commit changes

2. **Deploy to Raspberry Pi 5**
   - Copy application files to Raspberry Pi
   - Use the deployment guide to set up the application
   - Run as a service for production use

3. **Edit files on Raspberry Pi** (if needed)
   - Use alternative editors (see below)
   - Or use remote development tools

### Alternative Development Tools for Raspberry Pi 5

If you need to edit files directly on the Raspberry Pi, consider these alternatives:

#### Option 1: VS Code (Recommended)

VS Code has ARM64 builds that work on Raspberry Pi 5:

```bash
# Download VS Code for ARM64
wget -O code.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-arm64"

# Install
sudo dpkg -i code.deb
sudo apt-get install -f  # Fix any dependencies

# Launch
code
```

**VS Code Extensions for Python Development:**
- Python extension
- Pylance
- Python Debugger
- YAML extension (for config files)

#### Option 2: Remote Development via SSH

Use Cursor or VS Code on your main computer with Remote SSH:

1. **Install SSH on Raspberry Pi** (usually pre-installed):
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

2. **Connect from your main computer**:
   - Use VS Code Remote SSH extension
   - Or use Cursor's remote features (if available)
   - Connect to: `ssh pi@raspberry-pi-ip-address`

3. **Edit files remotely**:
   - Files are edited on your main computer
   - Changes are saved directly to Raspberry Pi
   - Run commands via integrated terminal

#### Option 3: Terminal-Based Editors

For quick edits or when GUI is not available:

**Nano** (Simple, beginner-friendly):
```bash
nano config/settings.yml
# Ctrl+O to save, Ctrl+X to exit
```

**Vim** (Powerful, learning curve):
```bash
vim config/settings.yml
# Press 'i' to insert, Esc then ':wq' to save and quit
```

**Neovim** (Modern Vim):
```bash
sudo apt install neovim
nvim config/settings.yml
```

#### Option 4: Web-Based Development

**Code-Server** (VS Code in browser):
```bash
# Install code-server
curl -fsSL https://code-server.dev/install.sh | sh

# Start code-server
code-server --bind-addr 0.0.0.0:8080

# Access via browser: http://raspberry-pi-ip:8080
```

**JupyterLab** (For Python development):
```bash
pip install jupyterlab
jupyter lab --ip=0.0.0.0
# Access via browser
```

### Recommended Development Setup

**Best Practice Workflow**:

1. **Primary Development**: Use Cursor IDE on your main computer
   - Full IDE features
   - Git integration
   - AI assistance
   - All extensions available

2. **Testing on Raspberry Pi**: Deploy and test on Pi
   - Copy files via Git, SCP, or shared folder
   - Test MIDI functionality
   - Verify Stream Deck operation

3. **Quick Edits on Pi**: Use VS Code or terminal editors
   - VS Code for GUI editing
   - Nano/Vim for quick terminal edits
   - Remote SSH for seamless workflow

### File Transfer Methods

To get files from your development machine to Raspberry Pi:

**Method 1: Git** (Recommended):
```bash
# On Raspberry Pi - Use the update script (recommended)
cd ~/devdeck
bash scripts/update/update-devdeck.sh

# Or manually:
cd ~/devdeck
git pull origin main
sudo systemctl restart devdeck.service
```

**Method 2: SCP** (Secure Copy):
```bash
# From your main computer
scp -r ~/devdeck/* pi@raspberry-pi-ip:~/devdeck/
```

**Method 3: Shared Folder** (Samba):
See the [Samba Configuration section](#samba-configuration-windows-network-access) for detailed setup instructions. This allows direct file access from Windows without copying files.

**Method 4: USB Drive**:
- Copy files to USB drive
- Mount on Raspberry Pi
- Copy files to application directory

## Development Workflow

When developing the application, you'll typically work on your main computer and test on the Raspberry Pi. This section explains the recommended workflow for updating code and managing the service.

### Overview

The recommended development workflow is:

1. **Develop locally** on your main computer (Windows/Mac/Linux) using your preferred IDE
2. **Commit and push** changes to your git repository
3. **Update on Raspberry Pi** using the provided update script
4. **Test and verify** the changes work correctly
5. **Manage the service** as needed during development

### Updating Code on Raspberry Pi

After making changes locally and pushing to git, update the code on your Raspberry Pi:

**Using the Update Script (Recommended):**

```bash
# On Raspberry Pi
cd ~/devdeck
bash scripts/update/update-devdeck.sh
```

This script will:
- Pull the latest code from git
- Warn you if there are uncommitted local changes
- Automatically restart the service
- Show the service status

**Manual Update:**

If you prefer to update manually:

```bash
# On Raspberry Pi
cd ~/devdeck

# Pull latest code
git pull origin main

# Restart the service
sudo systemctl restart devdeck.service

# Check status
sudo systemctl status devdeck.service
```

### Managing the Service During Development

The `manage-service.sh` script provides easy commands to control the service:

**Basic Service Control:**

```bash
# Restart service (after code updates)
bash scripts/manage/manage-service.sh restart

# Start service
bash scripts/manage/manage-service.sh start

# Stop service
bash scripts/manage/manage-service.sh stop

# Check service status
bash scripts/manage/manage-service.sh status
```

**Managing Autostart:**

During development, you may want to temporarily disable autostart to test manually:

```bash
# Disable autostart (service won't start on boot)
bash scripts/manage/manage-service.sh disable

# Enable autostart (service will start on boot)
bash scripts/manage/manage-service.sh enable

# Toggle autostart (convenient for switching)
bash scripts/manage/manage-service.sh toggle
```

**Viewing Logs:**

```bash
# Follow logs in real-time (Press Ctrl+C to exit)
bash scripts/manage/manage-service.sh logs

# View last 50 log lines
bash scripts/manage/manage-service.sh logs-last

# View logs since last boot
bash scripts/manage/manage-service.sh logs-boot
```

### Complete Development Workflow Example

Here's a complete example of the development workflow:

**1. On your development machine:**

```bash
# Make code changes in your IDE
# ... edit files ...

# Commit changes
git add .
git commit -m "Add new feature"
git push origin main
```

**2. On Raspberry Pi:**

```bash
# Update code and restart service
cd ~/devdeck
bash scripts/update/update-devdeck.sh
```

**3. Verify the changes:**

```bash
# Check service status
bash scripts/manage/manage-service.sh status

# View logs to verify it's working
bash scripts/manage/manage-service.sh logs
```

### Working with Uncommitted Changes

If you have uncommitted changes on the Raspberry Pi, the update script will warn you:

```bash
$ bash scripts/update/update-devdeck.sh
WARNING: You have uncommitted changes in your working directory.
These changes may be overwritten by git pull.
Continue anyway? (y/n)
```

**Options:**

- **Save your changes first:**
  ```bash
  git stash  # Temporarily save changes
  bash scripts/update/update-devdeck.sh
  git stash pop  # Restore changes if needed
  ```

- **Commit your changes:**
  ```bash
  git add .
  git commit -m "Local changes"
  bash scripts/update/update-devdeck.sh
  ```

- **Discard changes:**
  ```bash
  git reset --hard HEAD  # WARNING: This discards all uncommitted changes
  bash scripts/update/update-devdeck.sh
  ```

### Testing Without Service

If you want to test the application manually without the service running:

```bash
# Stop and disable the service
bash scripts/manage/manage-service.sh stop
bash scripts/manage/manage-service.sh disable

# Run manually
cd ~/devdeck
source venv/bin/activate
python -m devdeck.main

# When done, re-enable autostart
bash scripts/manage/manage-service.sh enable
bash scripts/manage/manage-service.sh start
```

### Troubleshooting Development Issues

**Service won't restart after update:**

```bash
# Check service status
bash scripts/manage/manage-service.sh status

# View error logs
bash scripts/manage/manage-service.sh logs-last

# Check for Python errors
cd ~/devdeck
source venv/bin/activate
python -m devdeck.main  # Run manually to see errors
```

**Git pull conflicts:**

If you have conflicts during `git pull`, resolve them manually:

```bash
cd ~/devdeck
git pull origin main
# Resolve conflicts in the files shown
git add .
git commit -m "Resolve merge conflicts"
sudo systemctl restart devdeck.service
```

**Service keeps restarting (crash loop):**

```bash
# Disable service temporarily
bash scripts/manage/manage-service.sh disable
bash scripts/manage/manage-service.sh stop

# Run manually to see the error
cd ~/devdeck
source venv/bin/activate
python -m devdeck.main

# Fix the issue, then re-enable
bash scripts/manage/manage-service.sh enable
bash scripts/manage/manage-service.sh start
```

## Additional Resources

### Useful Commands Reference

```bash
# Service management
sudo systemctl start|stop|restart|status devdeck.service

# Log viewing
sudo journalctl -u devdeck.service -f

# MIDI testing
aconnect -l
amidi -l
cd ~/devdeck && source venv/bin/activate && python3 tests/list_midi_ports.py

# USB debugging
lsusb
dmesg | tail
```

### Documentation Files

- `README.md` - Main project documentation
- `USER_GUIDE.md` - User guide for application usage
- `MIDI_IMPLEMENTATION.md` - MIDI implementation details

### Getting Help

1. Check application logs: `sudo journalctl -u devdeck.service`
2. Test MIDI connectivity: `python3 tests/devdeck/ketron/test_ketron_sysex.py`
3. Verify hardware connections: `lsusb`, `aconnect -l`
4. Check service status: `sudo systemctl status devdeck.service`

---

## Quick Start Checklist

Use this checklist for a quick deployment:

- [ ] Raspberry Pi 5 with OS installed and updated
- [ ] System dependencies installed (`libasound2-dev`, `libjack-dev`, etc.)
- [ ] Python virtual environment created and activated
- [ ] Application dependencies installed (`pip install -r requirements.txt`)
- [ ] Stream Deck connected and USB permissions configured
- [ ] MIDI device connected and detected (`aconnect -l`)
- [ ] Configuration files updated (`settings.yml`, `key_mappings.json`)
- [ ] Application tested manually (`python3 -m devdeck.main`)
- [ ] Systemd service created and enabled
- [ ] Service starts on boot and runs correctly
- [ ] Logs monitored for errors
- [ ] Backup strategy in place

---

*Last Updated: 2025*

**Note**: This guide assumes Raspberry Pi OS (64-bit). Adjustments may be needed for other Linux distributions.

To do: This file needs to be reviewed to ensure it is accurate

