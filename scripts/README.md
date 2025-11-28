# Scripts Directory

This directory contains utility scripts for the devdeck project.

## Development Workflow Scripts

### update-devdeck.sh

Updates the application from git and restarts the service. This is the recommended way to update code on your Raspberry Pi after making changes locally.

**Location:** `scripts/update/update-devdeck.sh`

**Usage:**

```bash
# From the project directory
bash scripts/update/update-devdeck.sh
```

**What it does:**
1. Checks for uncommitted changes (warns if found)
2. Performs `git pull` to get latest code
3. Restarts the devdeck service automatically
4. Shows service status

**Example Workflow:**

```bash
# On your development machine (Windows/Mac/Linux)
# ... make code changes ...
git add .
git commit -m "Add new feature"
git push origin main

# On Raspberry Pi
cd ~/devdeck
bash scripts/update/update-devdeck.sh
```

### manage-service.sh

Provides easy commands to manage the devdeck systemd service.

**Location:** `scripts/manage/manage-service.sh`

**Usage:**

```bash
bash scripts/manage/manage-service.sh [command]
```

**Commands:**

- `start` - Start the service
- `stop` - Stop the service
- `restart` - Restart the service
- `status` - Show service status
- `enable` - Enable service to start on boot
- `disable` - Disable service from starting on boot
- `toggle` - Toggle autostart (enable/disable)
- `logs` - Show service logs (follow mode, real-time)
- `logs-last` - Show last 50 log lines
- `logs-boot` - Show logs since last boot
- `help` - Show help message

**Examples:**

```bash
# Restart the service after code changes
bash scripts/manage/manage-service.sh restart

# Temporarily disable autostart for manual testing
bash scripts/manage/manage-service.sh disable

# Re-enable autostart
bash scripts/manage/manage-service.sh toggle

# View logs in real-time
bash scripts/manage/manage-service.sh logs

# Check if service is running
bash scripts/manage/manage-service.sh status
```

## Autostart Scripts

### install-logs-autostart.sh

Installs a desktop autostart entry that automatically opens a terminal window showing devdeck service logs when you log in to the desktop.

**Location:** `scripts/systemd/install-logs-autostart.sh`

**Usage:**

```bash
cd ~/devdeck
bash scripts/systemd/install-logs-autostart.sh
```

**What it does:**
1. Creates a desktop autostart entry in `~/.config/autostart/`
2. Opens a terminal window 5 seconds after login
3. Shows devdeck service logs in real-time
4. Keeps the terminal open for monitoring

**To disable:**
```bash
rm ~/.config/autostart/devdeck-logs.desktop
```

**Note**: This feature requires a desktop environment (Raspberry Pi OS Desktop). It won't work on headless systems.

## Utility Scripts

### generate_key_mappings.py

Generates a random JSON structure containing key mappings for all 30 keys (0-29) from the Ketron MIDI dictionaries (`pedal_midis`, `tab_midis`, or `cc_midis`).

**Usage:**

```bash
python scripts/generate/generate_key_mappings.py
```

The script will generate `config/key_mappings.json` with random mappings for all keys.

**Output Format:**

The generated JSON file has the following structure:

```json
{
  "key_mappings": [
    {
      "key_no": 0,
      "key_name": "Sustain",
      "source_list_name": "pedal_midis",
      "text_color": "white",
      "background_color": "black"
    },
    ...
  ]
}
```

