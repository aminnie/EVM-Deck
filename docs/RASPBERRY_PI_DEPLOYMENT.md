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
10. [Running as a Service](#running-as-a-service)
11. [Auto-Start Configuration](#auto-start-configuration)
12. [Testing and Verification](#testing-and-verification)
13. [Troubleshooting](#troubleshooting)
14. [Maintenance](#maintenance)
15. [Development on Raspberry Pi 5](#development-on-raspberry-pi-5)

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

Set up a shared folder on Raspberry Pi and access it from Windows:

**On Raspberry Pi:**
```bash
# Install Samba
sudo apt install -y samba samba-common-bin

# Create shared directory
sudo mkdir -p /home/pi/shared
sudo chmod 777 /home/pi/shared

# Configure Samba
sudo nano /etc/samba/smb.conf
```

Add to the end of the file:
```ini
[devdeck]
path = /home/pi/shared
writeable = yes
guest ok = yes
create mask = 0777
directory mask = 0777
```

```bash
# Restart Samba
sudo systemctl restart smbd

# Set Samba password for user pi
sudo smbpasswd -a pi
```

**On Windows:**
1. Open File Explorer
2. Navigate to: `\\raspberry-pi-ip\devdeck` (replace with Pi's IP)
3. Copy files from your development machine
4. Files will appear in `/home/pi/shared` on Raspberry Pi
5. Move to application directory:
   ```bash
   mv ~/shared/* ~/devdeck/
   ```

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
   - Connect Ketron device via USB
   - OR connect USB MIDI interface

2. **Verify MIDI Device Detection**:
   ```bash
   # List MIDI devices
   aconnect -l
   
   # List ALSA MIDI ports
   amidi -l
   
   # Check USB devices
   lsusb | grep -i midi
   ```

### Step 2: Test MIDI Communication

```bash
# Navigate to project root directory
cd ~/devdeck

# Activate virtual environment
source venv/bin/activate

# Test MIDI port listing (must be run from project root)
python3 scripts/list/list_midi_ports.py

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
python3 scripts/list/list_midi_ports.py

# Note the exact port name for your Ketron device
# Example: "MidiView 1" or "Ketron EVM MIDI 1"
```

### Common MIDI Port Names on Raspberry Pi

- USB MIDI devices often appear as: `"USB MIDI Device"` or device-specific names
- ALSA MIDI ports: `"MidiView 1"`, `"MidiView 2"`, etc.
- Check with `aconnect -l` for ALSA client names

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

# Test run (will show any errors)
python3 -m devdeck.main

# Press Ctrl+C to stop
```

---

## Running as a Service

### Step 1: Create Systemd Service File

```bash
# Create service file
sudo nano /etc/systemd/system/devdeck.service
```

Add the following content (adjust paths as needed):
```ini
[Unit]
Description=Ketron EVM Stream Deck Controller
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/devdeck
Environment="PATH=/home/pi/devdeck/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/devdeck/venv/bin/python -m devdeck.main
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

**Important**: Replace `/home/pi` with your actual home directory if different.

### Step 2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable devdeck.service

# Start service
sudo systemctl start devdeck.service

# Check status
sudo systemctl status devdeck.service
```

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

```bash
# Start service
sudo systemctl start devdeck.service

# Stop service
sudo systemctl stop devdeck.service

# Restart service
sudo systemctl restart devdeck.service

# Check status
sudo systemctl status devdeck.service

# Disable auto-start
sudo systemctl disable devdeck.service

# Enable auto-start
sudo systemctl enable devdeck.service
```

---

## Auto-Start Configuration

### Option 1: Systemd Service (Recommended)

The systemd service created above will automatically start on boot. This is the recommended method.

### Option 2: Crontab (Alternative)

If you prefer not to use systemd:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
@reboot cd /home/pi/devdeck && /home/pi/devdeck/venv/bin/python -m devdeck.main >> /home/pi/devdeck/logs/devdeck.log 2>&1
```

### Option 3: .bashrc or .profile (Not Recommended)

Not recommended for production, but can be used for testing:
```bash
# Add to ~/.bashrc (only if not using systemd)
# cd ~/devdeck && source venv/bin/activate && python -m devdeck.main &
```

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
python3 scripts/list/list_midi_ports.py

# Test Ketron SysEx
python3 tests/devdeck/ketron/test_ketron_sysex.py "Your MIDI Port Name"
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

### MIDI Port Not Found

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
python3 scripts/list/list_midi_ports.py
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

**Solutions**:

**Step 1: Check Pillow Version**
```bash
source venv/bin/activate
pip show pillow
# If version is 10.0.0 or higher, you need to fix devdeck-core
```

**Step 2: Fix devdeck-core text_renderer.py**
```bash
# Find the text_renderer.py file in devdeck-core
find ~/devdeck/venv -name "text_renderer.py" -path "*/devdeck_core/*"

# The file should be at:
# ~/devdeck/venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py

# Edit the file
nano ~/devdeck/venv/lib/python3.*/site-packages/devdeck_core/rendering/text_renderer.py
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

**Note**: This fix is applied to your local virtual environment. If you recreate the venv or reinstall `devdeck-core`, you'll need to reapply this fix. Consider submitting a patch to the `devdeck-core` project for a permanent solution.

**Common Causes**:
- Pillow 10.0.0+ installed (textsize() method removed)
- devdeck-core package not updated for Pillow 10.0.0+

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
python3 scripts/list/list_midi_ports.py

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
# On Raspberry Pi
cd ~/devdeck
git pull origin main
```

**Method 2: SCP** (Secure Copy):
```bash
# From your main computer
scp -r ~/devdeck/* pi@raspberry-pi-ip:~/devdeck/
```

**Method 3: Shared Folder** (Samba):
```bash
# Install Samba on Pi
sudo apt install samba

# Configure shared folder
sudo nano /etc/samba/smb.conf

# Access from Windows: \\raspberry-pi-ip\devdeck
```

**Method 4: USB Drive**:
- Copy files to USB drive
- Mount on Raspberry Pi
- Copy files to application directory

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
cd ~/devdeck && source venv/bin/activate && python3 scripts/list/list_midi_ports.py

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

