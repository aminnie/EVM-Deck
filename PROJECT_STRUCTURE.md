# Project Structure

This document describes the organization and structure of the devdeck project.

## Directory Structure

```
devdeck-main/
├── bin/                    # Utility binaries and scripts
│   └── device_info.py     # Device information utility
│
├── config/                 # Configuration files
│   ├── key_mappings.json   # Key-to-MIDI command mappings
│   ├── settings.yml.backup # Backup of settings file
│   └── README.md          # Config directory documentation
│
├── devdeck/                # Main package directory
│   ├── assets/            # Static assets (icons, fonts, etc.)
│   │   └── font-awesome/  # Font Awesome icons
│   │
│   ├── controls/          # Stream Deck control implementations
│   │   ├── clock_control.py
│   │   ├── command_control.py
│   │   ├── mic_mute_control.py
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
│   ├── examples/          # Example code
│   │   └── update_text_example.py
│   │
│   ├── settings/          # Settings management
│   │   ├── control_settings.py
│   │   ├── deck_settings.py
│   │   ├── devdeck_settings.py
│   │   └── validation_error.py
│   │
│   ├── deck_context.py    # Deck context management
│   ├── deck_manager.py    # Deck manager
│   ├── filters.py         # Logging filters
│   ├── ketron.py          # Ketron MIDI definitions
│   └── main.py            # Main entry point
│
├── icons/                  # Icon resources
│
├── scripts/               # Utility scripts
│   ├── generate_key_mappings.py  # Generate random key mappings
│   └── README.md          # Scripts documentation
│
├── tests/                 # Test suite
│   └── devdeck/          # Tests for devdeck package
│       ├── controls/     # Control tests
│       └── settings/     # Settings tests
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
├── setup.sh              # Setup script for development
└── PROJECT_STRUCTURE.md  # This file
```

## Key Directories

### `config/`
Contains configuration files that are used by the application:
- **key_mappings.json**: Defines mappings between Stream Deck keys and MIDI commands
- **settings.yml.backup**: Backup copies of settings files

### `scripts/`
Utility scripts for development and maintenance:
- **generate_key_mappings.py**: Generates random key mappings for testing

### `devdeck/`
Main package containing all application code:
- **controls/**: Individual Stream Deck button controls
- **decks/**: Deck controller implementations (layouts)
- **settings/**: Configuration management
- **ketron.py**: MIDI command definitions for Ketron devices

### `tests/`
Test suite following the same structure as the main package.

## File Organization Principles

1. **Separation of Concerns**: 
   - Library code in `devdeck/`
   - Utility scripts in `scripts/`
   - Configuration in `config/`

2. **Configuration Files**:
   - Main `settings.yml` in project root (for easy access)
   - Generated/backup files in `config/`

3. **Scripts**:
   - All utility scripts in `scripts/` directory
   - Scripts are executable and self-contained

4. **Documentation**:
   - README files in each major directory
   - This file for overall structure

## Best Practices

1. **Import Paths**: Scripts use proper path manipulation to import from `devdeck` package
2. **Configuration**: Configuration files are organized and documented
3. **Backups**: Backup files are stored in `config/` directory
4. **Git Ignore**: Comprehensive `.gitignore` excludes build artifacts, caches, and temporary files

## Adding New Files

- **New Controls**: Add to `devdeck/controls/`
- **New Decks**: Add to `devdeck/decks/`
- **New Scripts**: Add to `scripts/`
- **New Config**: Add to `config/` (or project root if it's the main settings file)
- **New Tests**: Mirror structure in `tests/devdeck/`

