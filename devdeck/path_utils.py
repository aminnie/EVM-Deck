"""
Path utilities for detecting bundle vs development mode and returning correct paths.

This module helps the application work correctly both in development mode
and when packaged as a macOS .app bundle.
"""

import sys
import os
from pathlib import Path
from typing import Optional


def is_bundled() -> bool:
    """
    Check if the application is running from a bundled .app on macOS.
    
    Returns:
        True if running from a .app bundle, False otherwise
    """
    # py2app sets sys.frozen to True when bundled
    if getattr(sys, 'frozen', False):
        return True
    
    # Additional check: if running on macOS and the executable path contains .app
    if sys.platform == 'darwin':
        # Check if we're inside a .app bundle structure
        # In a bundle, __file__ or sys.executable will be inside .app/Contents/
        executable_path = Path(sys.executable)
        if '.app/Contents/' in str(executable_path) or '.app/Contents/' in str(Path(__file__).resolve()):
            return True
    
    return False


def get_project_root() -> Path:
    """
    Get the project root directory, handling both development and bundled modes.
    
    In development mode, this is the parent of the devdeck package.
    In bundled mode, this is the Resources directory inside the .app bundle.
    
    Returns:
        Path to the project root directory
    """
    if is_bundled():
        # In a py2app bundle, resources are in Contents/Resources/
        # sys.executable points to Contents/MacOS/DevDeck
        # We need to go up to Contents, then into Resources
        if sys.platform == 'darwin':
            # Get the bundle root (Contents directory)
            executable = Path(sys.executable)
            # executable is at Contents/MacOS/DevDeck
            # bundle_root is at Contents/
            bundle_root = executable.parent.parent  # Contents/
            resources_dir = bundle_root / 'Resources'
            
            # The project root in the bundle is the Resources directory
            # where all Python packages and assets are located
            return resources_dir
        else:
            # For other platforms (shouldn't happen with py2app, but handle gracefully)
            return Path(sys.executable).parent
    
    # Development mode: go up from devdeck package to project root
    # This file is at devdeck/path_utils.py
    # Project root is one level up
    return Path(__file__).parent.parent


def get_config_dir() -> Path:
    """
    Get the configuration directory.
    
    In development mode, this is config/ in the project root.
    In bundled mode, this is also config/ in Resources, but user configs
    should be stored in ~/.devdeck/ for persistence.
    
    Returns:
        Path to the configuration directory
    """
    project_root = get_project_root()
    
    if is_bundled():
        # In bundle, check Resources/config first (for templates/defaults)
        # But user configs should go to ~/.devdeck/
        config_dir = project_root / 'config'
        if config_dir.exists():
            return config_dir
        # Fallback to user directory for bundled app
        return Path.home() / '.devdeck'
    
    # Development mode: use config/ in project root
    return project_root / 'config'


def get_assets_dir() -> Path:
    """
    Get the assets directory.
    
    Returns:
        Path to the assets directory
    """
    project_root = get_project_root()
    
    if is_bundled():
        # In bundle, assets are in Resources/devdeck/assets/
        assets_dir = project_root / 'devdeck' / 'assets'
        if assets_dir.exists():
            return assets_dir
        # Fallback to Resources/assets/ if structure is different
        return project_root / 'assets'
    
    # Development mode: assets are in devdeck/assets/
    return project_root / 'devdeck' / 'assets'


def get_logs_dir() -> Path:
    """
    Get the logs directory.
    
    In development mode, this is logs/ in the project root.
    In bundled mode, logs should go to ~/.devdeck/logs/ for persistence.
    
    Returns:
        Path to the logs directory
    """
    if is_bundled():
        # In bundle, use user directory for logs (persistent across updates)
        logs_dir = Path.home() / '.devdeck' / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    # Development mode: use logs/ in project root
    project_root = get_project_root()
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

