# Scripts Directory

This directory contains utility scripts for the devdeck project.

## generate_key_mappings.py

Generates a random JSON structure containing key mappings for all 30 keys (0-29) from the Ketron MIDI dictionaries (`pedal_midis`, `tab_midis`, or `cc_midis`).

### Usage

```bash
python scripts/generate_key_mappings.py
```

The script will generate `config/key_mappings.json` with random mappings for all keys.

### Output Format

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

