# Project Structure

This document describes the organization and structure of the devdeck project.

## Directory Structure

```
devdeck-main/
├── bin/                    # (Deprecated - moved to scripts/bin/)
│
├── config/                 # Configuration files
│   ├── key_mappings.json   # Key-to-MIDI command mappings
│   ├── settings.yml.backup # Backup of settings file
│   └── settings.yml.template # Settings template
│
├── devdeck/                # Main package directory
│   ├── assets/            # Static assets (icons, fonts, etc.)
│   │   ├── EVM-KETRON.jpeg
│   │   └── font-awesome/  # Font Awesome icons
│   │
│   ├── controls/          # General Stream Deck control implementations
│   │   ├── clock_control.py
│   │   ├── command_control.py
│   │   ├── mic_mute_control.py
│   │   ├── midi_control.py
│   │   ├── name_list_control.py
│   │   ├── navigation_toggle_control.py
│   │   ├── text_control.py
│   │   ├── timer_control.py
│   │   ├── volume_level_control.py
│   │   └── volume_mute_control.py
│   │
│   ├── decks/             # Deck controller implementations
│   │   ├── second_page_deck_controller.py
│   │   ├── single_page_deck_controller.py
│   │   └── volume_deck.py
│   │
│   ├── ketron/            # Ketron-specific functionality
│   │   ├── __init__.py
│   │   ├── ketron.py          # Ketron MIDI definitions
│   │   ├── ketron_volume_manager.py
│   │   └── controls/
│   │       ├── __init__.py
│   │       └── ketron_key_mapping_control.py
│   │
│   ├── examples/          # Example code
│   │   ├── README.md      # Examples documentation
│   │   ├── controls/      # Control examples
│   │   │   └── update_text_example.py
│   │   └── midi/          # MIDI examples
│   │       └── midi_control_example.py
│   │
│   ├── settings/          # Settings management
│   │   ├── control_settings.py
│   │   ├── deck_settings.py
│   │   ├── devdeck_settings.py
│   │   └── validation_error.py
│   │
│   ├── ketron/            # Ketron-specific functionality
│   │   ├── __init__.py
│   │   ├── ketron.py          # Ketron MIDI definitions
│   │   ├── ketron_volume_manager.py
│   │   └── controls/
│   │       ├── __init__.py
│   │       └── ketron_key_mapping_control.py
│   │
│   ├── midi/              # MIDI infrastructure
│   │   ├── __init__.py
│   │   ├── midi_manager.py
│   │   └── controls/
│   │       ├── __init__.py
│   │       └── midi_control.py
│   │
│   ├── deck_context.py    # Deck context management
│   ├── deck_manager.py    # Deck manager
│   ├── filters.py         # Logging filters
│   └── main.py            # Main entry point
│
├── docs/                   # Documentation
│   ├── USER_GUIDE.md
│   ├── RASPBERRY_PI_DEPLOYMENT.md
│   ├── MIDI_IMPLEMENTATION.md
│   ├── PROJECT_STRUCTURE.md
│   └── config/
│       └── README.md
│
├── scripts/               # Utility scripts
│   ├── bin/               # Binary/executable utilities
│   │   └── device_info.py
│   ├── check/             # Verification/check scripts
│   │   ├── check_app_midi_identity.py
│   │   ├── check_midi_identity.py
│   │   └── check_windows_midi.ps1
│   ├── generate/          # Code generation scripts
│   │   └── generate_key_mappings.py
│   ├── list/              # Listing utilities
│   │   └── list_midi_ports.py
│   └── run/               # Run scripts
│       ├── run-devdeck.bat
│       ├── run-devdeck.ps1
│       ├── run-devdeck.sh
│       ├── run-pylint.sh
│       └── run-tests.sh
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test-icon.png
│   ├── testing_utils.py
│   └── devdeck/          # Tests for devdeck package
│       ├── controls/     # Control tests
│       ├── ketron/       # Ketron tests
│       │   ├── test_ketron_sysex.py
│       │   └── test_ketron_volume_manager.py
│       ├── midi/         # MIDI tests
│       │   ├── test_midi.py
│       │   └── test_midi_connectivity.py
│       ├── settings/     # Settings tests
│       └── test_deck_manager.py
│
├── settings.yml           # Main configuration file (project root)
│
├── .gitignore            # Git ignore rules
├── LICENSE               # License file
├── MANIFEST.in           # Package manifest
├── pyproject.toml         # Python project configuration
├── README.md             # Main project documentation
├── requirements.txt      # Python dependencies
├── setup.py              # Package setup script
└── setup.sh              # Setup script for development
```

## Key Directories

### `config/`
Contains configuration files that are used by the application:
- **key_mappings.json**: Defines mappings between Stream Deck keys and MIDI commands
- **settings.yml.backup**: Backup copies of settings files
- **settings.yml.template**: Template for settings file

### `scripts/`
Utility scripts organized by category:
- **bin/**: Binary/executable utilities
- **check/**: Verification and check scripts
- **generate/**: Code generation scripts
- **list/**: Listing utilities
- **run/**: Application and test run scripts

### `devdeck/`
Main package containing all application code:
- **controls/**: General Stream Deck button controls
- **decks/**: Deck controller implementations (layouts)
- **examples/**: Example code organized by category (controls, midi)
- **ketron/**: Ketron-specific functionality (MIDI, volume management, controls)
- **midi/**: MIDI infrastructure (manager and controls)
- **settings/**: Configuration management

### `docs/`
All project documentation:
- **USER_GUIDE.md**: User documentation
- **RASPBERRY_PI_DEPLOYMENT.md**: Deployment guide
- **MIDI_IMPLEMENTATION.md**: MIDI implementation details
- **PROJECT_STRUCTURE.md**: This file

### `tests/`
Test suite following the same structure as the main package:
- **controls/**: Tests for general controls
- **ketron/**: Tests for Ketron-specific functionality
- **midi/**: Tests for MIDI infrastructure
- **settings/**: Tests for settings management

## File Organization Principles

1. **Separation of Concerns**: 
   - Library code in `devdeck/`
   - Utility scripts in `scripts/` (organized by category)
   - Configuration in `config/`
   - Documentation in `docs/`

2. **Configuration Files**:
   - Main `settings.yml` in project root (for easy access)
   - Generated/backup files in `config/`

3. **Scripts**:
   - All utility scripts in `scripts/` directory, organized by purpose
   - Scripts are executable and self-contained

4. **Documentation**:
   - All documentation files in `docs/` directory
   - README files in each major directory where needed

5. **Ketron-Specific Code**:
   - All Ketron-related functionality in `devdeck/ketron/`
   - Includes MIDI definitions, volume management, and Ketron-specific controls

## Best Practices

1. **Import Paths**: Scripts use proper path manipulation to import from `devdeck` package
2. **Configuration**: Configuration files are organized and documented
3. **Backups**: Backup files are stored in `config/` directory
4. **Git Ignore**: Comprehensive `.gitignore` excludes build artifacts, caches, and temporary files
5. **Package Organization**: Related functionality is grouped into subpackages (e.g., `ketron/`)

## Adding New Files

- **New Controls**: 
  - General controls: Add to `devdeck/controls/`
  - Ketron-specific controls: Add to `devdeck/ketron/controls/`
- **New Decks**: Add to `devdeck/decks/`
- **New Scripts**: Add to appropriate subdirectory in `scripts/`
- **New Config**: Add to `config/` (or project root if it's the main settings file)
- **New Tests**: Mirror structure in `tests/devdeck/` (e.g., `tests/devdeck/ketron/` for Ketron tests)
- **New Documentation**: Add to `docs/`
- **New Examples**: Add to appropriate subdirectory in `devdeck/examples/` (e.g., `controls/` or `midi/`)

## Import Paths

### Ketron Code
```python
from devdeck.ketron import KetronMidi, KetronVolumeManager, COLOR_MAP
from devdeck.ketron.controls.ketron_key_mapping_control import KetronKeyMappingControl
```

### General Controls
```python
from devdeck.controls.text_control import TextControl
from devdeck.midi.controls.midi_control import MidiControl
```

### MIDI Infrastructure
```python
from devdeck.midi import MidiManager
```

### Running Scripts
```bash
# List MIDI ports
python scripts/list/list_midi_ports.py

# Check MIDI identity
python scripts/check/check_app_midi_identity.py

# Run application
python scripts/run/run-devdeck.sh
```
