"""
macOS packaging setup for DevDeck using py2app.

This script configures py2app to create a self-contained .app bundle
with bundled Python runtime, dependencies, and system libraries.
"""

from setuptools import setup
import sys
import os

# Ensure we're on macOS
if sys.platform != 'darwin':
    raise RuntimeError("This setup script is only for macOS")

# Temporarily rename pyproject.toml to prevent setuptools from reading it
# This avoids conflicts between py2app setup and pyproject.toml configuration
_pyproject_backup = None
if os.path.exists('pyproject.toml'):
    _pyproject_backup = 'pyproject.toml.backup'
    if os.path.exists(_pyproject_backup):
        os.remove(_pyproject_backup)
    os.rename('pyproject.toml', _pyproject_backup)

APP = ['devdeck/main.py']
# Include config directory if it has template files
DATA_FILES = []
if os.path.exists('config/settings.yml.template'):
    DATA_FILES.append(('config', ['config/settings.yml.template']))

# Check for icon file
ICON_FILE = 'devdeck/assets/icon.icns'
if not os.path.exists(ICON_FILE):
    print(f"Warning: Icon file not found: {ICON_FILE}")
    print("  Run 'python3 scripts/build/generate-icon.py' to generate the icon.")
    print("  Continuing without icon...")
    ICON_FILE = None

OPTIONS = {
    'argv_emulation': False,  # Don't use argv emulation (we handle sys.argv ourselves)
    'semi_standalone': False,  # Fully standalone bundle
    'alias': False,  # Create a full application, not an alias
    'packages': [
        'devdeck',
        'devdeck_core',
        'StreamDeck',
        'mido',
        'rtmidi',
        'PIL',
        'yaml',
        'cerberus',
        'jsonschema',
        'requests',
        'emoji',
        'pulsectl',
        'assertpy',
    ],
    'includes': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'logging',
        'logging.handlers',
        'threading',
        'queue',
        'pathlib',
        'json',
        'datetime',
    ],
    'excludes': [
        'pytest',
        'test',
        'tests',
        'unittest',
        'distutils',
    ],
    'iconfile': ICON_FILE,  # Path to .icns file
    'plist': {
        'CFBundleName': 'DevDeck',
        'CFBundleDisplayName': 'DevDeck',
        'CFBundleGetInfoString': 'DevDeck - Stream Deck MIDI Controller',
        'CFBundleIdentifier': 'com.devdeck.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
        'LSMinimumSystemVersion': '10.13',  # macOS High Sierra minimum
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        # USB device access (may need user permission)
        'NSUSBUsageDescription': 'DevDeck requires USB access to communicate with Elgato Stream Deck and MIDI devices.',
    },
    'resources': [
        'devdeck/assets',
        'config',
    ],
    'frameworks': [],  # System frameworks will be handled by build script
    'site_packages': True,  # Include site-packages
    'optimize': 0,  # Don't optimize bytecode (helps with debugging)
}

try:
    setup(
        app=APP,
        name='DevDeck',
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
finally:
    # Restore pyproject.toml if we renamed it
    if _pyproject_backup and os.path.exists(_pyproject_backup):
        if os.path.exists('pyproject.toml'):
            os.remove('pyproject.toml')
        os.rename(_pyproject_backup, 'pyproject.toml')

