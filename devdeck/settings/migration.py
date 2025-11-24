"""
Settings migration module for handling settings file location migration.

This module handles migration of settings files from old locations to the
new config directory location.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional


class SettingsMigrator:
    """Handles migration of settings files from old locations to new location."""
    
    @staticmethod
    def migrate_settings(project_root: Path, config_dir: Path, settings_filename: Path) -> bool:
        """
        Migrate settings file from old locations to new location.
        
        Args:
            project_root: Path to project root directory
            config_dir: Path to config directory (destination)
            settings_filename: Path to target settings file
            
        Returns:
            True if migration occurred, False otherwise
        """
        logger = logging.getLogger('devdeck')
        
        # If settings file already exists in new location, no migration needed
        if settings_filename.exists():
            return False
        
        # Ensure config directory exists
        config_dir.mkdir(exist_ok=True)
        
        # Define old locations in order of preference (most recent first)
        old_locations = [
            project_root / 'settings.yml',  # Project root (most recent)
            Path.home() / 'devdeck' / 'settings.yml',  # Home devdeck directory
            Path.home() / '.devdeck' / 'settings.yml',  # Hidden .devdeck directory
        ]
        
        # Try to migrate from each old location
        for old_path in old_locations:
            if old_path.exists():
                try:
                    logger.info("Migrating settings file from %s to %s", old_path, settings_filename)
                    shutil.move(str(old_path), str(settings_filename))
                    return True
                except Exception as e:
                    logger.error("Failed to migrate settings from %s: %s", old_path, e)
                    continue
        
        return False

