# Config Directory

This directory contains configuration files for the devdeck project.

## Files

- **key_mappings.json**: Contains mappings between Stream Deck keys and Ketron MIDI commands. This file is used to automatically update `settings.yml` on startup.
- **settings.yml.backup**: Backup of the settings file (if created).

## key_mappings.json

This file defines which MIDI command is assigned to each Stream Deck key. The structure includes:

- `key_no`: The key number (0-29, supporting 2 pages of 15 keys each)
- `key_name`: The name of the MIDI command
- `source_list_name`: The source list (`pedal_midis`, `tab_midis`, or `cc_midis`)
- `text_color`: Text color for the key display (default: "white")
- `background_color`: Background color for the key display (default: "black")

On startup, devdeck reads this file and updates the `settings.yml` file accordingly.

## Generating New Mappings

To generate a new random set of mappings:

```bash
python scripts/generate_key_mappings.py
```

This will overwrite the existing `key_mappings.json` file.

