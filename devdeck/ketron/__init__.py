"""
Ketron-specific MIDI functionality.

This package contains Ketron device-specific implementations including:
- MIDI command definitions
- Volume management
- Ketron-specific controls
"""

from devdeck.ketron.ketron import KetronMidi, COLOR_MAP
from devdeck.ketron.ketron_volume_manager import KetronVolumeManager

__all__ = ['KetronMidi', 'KetronVolumeManager', 'COLOR_MAP']

