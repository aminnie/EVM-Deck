"""
GUI Control Panel for EVMDeck Application

Provides a simple GUI interface to:
- Control application start, stop, and restart
- Monitor MIDI key presses
- Display connected MIDI input and output devices
"""

import json
import logging
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

try:
    import mido
except ImportError:
    mido = None

from devdeck.midi import MidiManager
from devdeck.usb_device_checker import check_elgato_stream_deck, check_midi_output_device
from devdeck.gui.key_press_queue import get_queue
from devdeck.deck_context import DeckContext
from devdeck.settings.devdeck_settings import DevDeckSettings
from devdeck.ketron.ketron import KetronMidi

# Try to import deck manager registry for screen clearing
try:
    from devdeck.gui.deck_manager_registry import get_deck_manager
    _DECK_MANAGER_REGISTRY_AVAILABLE = True
except ImportError:
    _DECK_MANAGER_REGISTRY_AVAILABLE = False
    get_deck_manager = None
from StreamDeck.DeviceManager import DeviceManager


class DevDeckControlPanel:
    """Main GUI control panel for EVMDeck application"""
    
    # Vendor ID to vendor name lookup table
    VENDOR_ID_LOOKUP = {
        '239a': 'Adafruit',
        '157b': 'Ketron',
        '0fd9': 'Elgato',
        '1a86': 'CH345',
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("EVMDeck Control Panel")
        self.root.geometry("480x320")
        self.root.resizable(True, True)
        
        self.logger = logging.getLogger('devdeck')
        
        # Application control state
        self.app_thread: Optional[threading.Thread] = None
        self.app_running = False
        self.app_stop_event = threading.Event()
        self.app_process = None  # For tracking the application process if needed
        
        # MIDI monitoring state
        self.midi_input_thread: Optional[threading.Thread] = None
        self.midi_input_port = None
        self.midi_monitoring = False
        self.midi_stop_event = threading.Event()
        self.midi_message_queue = queue.Queue()
        
        # Stream Deck key press monitoring
        self.streamdeck_key_queue = get_queue()
        self.key_mappings: Dict[int, str] = {}  # key_no -> key_name
        self._load_key_mappings()
        
        # MIDI manager - lazy initialization to avoid GIL issues
        self._midi_manager = None
        
        # Flag to prevent MIDI operations during initialization
        self._midi_ready = False
        
        # Build UI
        self._build_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Don't auto-update USB devices on startup to avoid GIL/threading issues
        # User can click "Refresh Devices" button to manually update
        # Set initial placeholder text
        self.usb_input_label.config(text="Click 'Refresh Devices' to scan", 
                                    foreground="gray")
        self.usb_output_label.config(text="Click 'Refresh Devices' to scan", 
                                     foreground="gray")
        
        # Mark MIDI as ready after GUI is fully initialized
        # Use a longer delay to ensure Python runtime is fully ready
        self.root.after(500, lambda: setattr(self, '_midi_ready', True))
        
        # Start MIDI message processing (defer to avoid blocking initialization)
        self.root.after(100, self._process_midi_messages)
    
    @property
    def midi_manager(self):
        """Lazy initialization of MidiManager to avoid GIL issues during GUI init"""
        if self._midi_manager is None:
            try:
                self._midi_manager = MidiManager()
            except Exception as e:
                self.logger.error(f"Failed to initialize MidiManager: {e}", exc_info=True)
                # Return a dummy object that has the methods we need
                class DummyMidiManager:
                    def get_open_ports(self):
                        return []
                self._midi_manager = DummyMidiManager()
        return self._midi_manager
    
    def _build_ui(self):
        """Build the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="EVMDeck Control Panel", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 2))
        
        # Application Control Section with status on title line
        control_frame = ttk.LabelFrame(main_frame, padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        control_frame.columnconfigure(1, weight=1)
        
        # Title and status on same line
        title_frame = ttk.Frame(control_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        title_frame.columnconfigure(1, weight=1)
        
        ttk.Label(title_frame, text="Application Control", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(title_frame, text="Status: Stopped", 
                                      foreground="red", font=("Arial", 11, "bold"))
        self.status_label.grid(row=0, column=1, padx=(20, 0), sticky=tk.E)
        
        # Control buttons and refresh button on same line
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(1, weight=1)  # Center column expands
        
        self.start_button = ttk.Button(button_frame, text="Start", 
                                       command=self._start_application, width=12)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Refresh Devices button centered
        refresh_button = ttk.Button(button_frame, text="Refresh Devices", 
                                    command=self._update_usb_devices, width=15)
        refresh_button.grid(row=0, column=1, padx=5)
        
        self.exit_button = ttk.Button(button_frame, text="Exit", 
                                     command=self._on_closing, width=12)
        self.exit_button.grid(row=0, column=2, padx=5)
        
        # USB Devices Section (no title)
        devices_frame = ttk.Frame(main_frame, padding="5")
        devices_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        devices_frame.columnconfigure(1, weight=1)
        
        # USB Input Device (Elgato Stream Deck)
        ttk.Label(devices_frame, text="USB Input Device:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.usb_input_label = ttk.Label(devices_frame, text="None", 
                                          foreground="gray", font=("Arial", 11))
        self.usb_input_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 3))
        
        # USB Output Device (MIDI output) with Start/Stop button
        ttk.Label(devices_frame, text="USB Output Device:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.usb_output_label = ttk.Label(devices_frame, text="None", 
                                           foreground="gray", font=("Arial", 11))
        self.usb_output_label.grid(row=1, column=1, sticky=tk.W)
        
        # Start/Stop button next to USB output device
        self.start_stop_button = ttk.Button(devices_frame, text="Start/Stop",
                                            command=self._send_start_stop, width=12)
        self.start_stop_button.grid(row=1, column=2, padx=(10, 0), sticky=tk.W)
        
        # MIDI Key Monitor Section with border (no title)
        monitor_frame = ttk.LabelFrame(main_frame, padding="5")
        monitor_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Scrolled text for MIDI messages (3 rows visible)
        self.midi_text = scrolledtext.ScrolledText(monitor_frame, height=3, 
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.midi_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _start_application(self):
        """Start the EVMDeck application in a separate thread"""
        if self.app_running:
            return
        
        self.app_running = True
        self.app_stop_event.clear()
        
        def run_app():
            try:
                self.logger.info("Starting EVMDeck application in background thread...")
                # Import here to avoid circular import and blocking during GUI init
                # Use a fresh import to avoid any cached state
                import importlib
                main_module = importlib.import_module('devdeck.main')
                devdeck_main = main_module.main
                
                # Note: This will run the main() function
                # We may need to modify main() to check for stop events
                devdeck_main()
            except KeyboardInterrupt:
                self.logger.info("Application interrupted by user")
            except Exception as e:
                error_msg = str(e)
                # Check if it's a device already open error
                if "Could not open HID device" in error_msg or "TransportError" in error_msg:
                    self.logger.warning("Stream Deck device appears to be locked. This may happen if:")
                    self.logger.warning("1. The device wasn't properly closed from a previous run")
                    self.logger.warning("2. Another application is using the device")
                    self.logger.warning("3. The device needs a moment to be released")
                    # Show user-friendly error in GUI
                    self.root.after(0, lambda: self._update_status("Error: Device locked", "red"))
                    self.root.after(0, lambda: self.status_label.config(
                        text="Status: Error - Device locked (try unplugging/replugging)", 
                        foreground="red"
                    ))
                else:
                    self.logger.error(f"Error in application thread: {e}", exc_info=True)
                    self.root.after(0, lambda: self._update_status("Error", "red"))
            finally:
                self.app_running = False
                # Only update status if it's not already set to a specific error
                current_status = self.status_label.cget("text")
                if "Error" not in current_status:
                    self.root.after(0, lambda: self._update_status("Stopped", "red"))
                self.root.after(0, self._update_buttons)
        
        self.app_thread = threading.Thread(target=run_app, daemon=True)
        self.app_thread.start()
        
        # Automatically start MIDI monitoring when application starts
        self._start_midi_monitoring()
        
        self._update_status("Running", "green")
        self._update_buttons()
    
    def _stop_application(self):
        """Stop the EVMDeck application"""
        if not self.app_running:
            return
        
        self._update_status("Stopping...", "orange")
        self._update_buttons()
        
        # Stop MIDI monitoring when application stops
        self._stop_midi_monitoring()
        
        # Set stop event
        self.app_stop_event.set()
        
        # Note: The main() function blocks on thread.join() which can't be interrupted
        # We'll wait a short time, then mark as stopped even if thread is still running
        # The thread is daemon=True so it will be killed when GUI exits
        stop_timeout_ms = 2000  # 2 seconds timeout
        check_interval = 100  # Check every 100ms
        max_checks = stop_timeout_ms // check_interval
        check_count = [0]  # Use list to allow modification in nested function
        
        def check_thread():
            check_count[0] += 1
            
            if self.app_thread and self.app_thread.is_alive():
                if check_count[0] < max_checks:
                    # Thread still running, check again
                    self.root.after(check_interval, check_thread)
                else:
                    # Timeout reached - thread didn't exit cleanly
                    # This is expected since main() blocks on join() with no timeout
                    self.logger.warning("Application thread did not exit within timeout - marking as stopped")
                    self.app_running = False
                    self._update_status("Stopped", "red")
                    self._update_buttons()
                    self.logger.info("Application marked as stopped (daemon thread will be cleaned up on exit)")
            else:
                # Thread finished cleanly
                self.app_running = False
                self._update_status("Stopped", "red")
                self._update_buttons()
                self.logger.info("Application stopped cleanly")
        
        self.root.after(check_interval, check_thread)
    
    def _restart_application(self):
        """Restart the EVMDeck application"""
        if self.app_running:
            # First stop the application
            self._stop_application()
            
            # Wait for stop to complete, then restart
            # We need to wait for both the stop operation and device release
            restart_delay_ms = 3000  # 3 seconds total (2s for stop timeout + 1s for device release)
            check_interval = 200  # Check every 200ms
            max_checks = restart_delay_ms // check_interval
            check_count = [0]  # Use list to allow modification in nested function
            
            def wait_and_restart():
                check_count[0] += 1
                
                if self.app_running:
                    # Still stopping, wait a bit more
                    if check_count[0] < max_checks:
                        self.root.after(check_interval, wait_and_restart)
                    else:
                        # Timeout - force stop and restart anyway
                        self.logger.warning("Restart timeout - forcing stop and restart")
                        self.app_running = False
                        self._update_status("Stopped", "red")
                        self._update_buttons()
                        # Wait a moment for device release, then restart
                        self.logger.info("Waiting for device release before restart...")
                        self.root.after(1500, lambda: self._start_application())
                else:
                    # Stopped, wait a moment for device release, then restart
                    self.logger.info("Application stopped, waiting for device release before restart...")
                    self.root.after(1500, lambda: self._start_application())
            
            self.root.after(check_interval, wait_and_restart)
        else:
            # Not running, just start it
            self._start_application()
    
    def _update_status(self, status: str, color: str):
        """Update the status label"""
        self.status_label.config(text=f"Status: {status}", foreground=color)
    
    def _update_buttons(self):
        """Update button states based on application state"""
        if self.app_running:
            self.start_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
    
    def _safe_midi_call(self, func, default=None):
        """
        Safely execute a MIDI-related function, handling GIL/threading issues.
        
        This method attempts to catch fatal errors from the rtmidi C extension
        which can cause Python to abort on macOS.
        
        Args:
            func: Callable that performs MIDI operation
            default: Default value to return if operation fails
        
        Returns:
            Result of func() or default if operation fails
        """
        try:
            # Try to execute the function
            return func()
        except (RuntimeError, SystemError) as e:
            error_msg = str(e).lower()
            if "gil" in error_msg or "thread" in error_msg or "null" in error_msg:
                self.logger.warning(f"MIDI operation failed due to threading/GIL issue: {e}")
            else:
                self.logger.error(f"MIDI operation failed: {e}")
            return default
        except Exception as e:
            # Catch any other exceptions
            self.logger.error(f"MIDI operation error: {e}")
            return default
    
    def _get_vendor_name(self, vendor_id: str) -> str:
        """
        Look up vendor name from vendor ID.
        
        Args:
            vendor_id: Vendor ID string (e.g., '0fd9')
        
        Returns:
            Vendor name if found, otherwise returns the vendor_id
        """
        if vendor_id:
            vendor_id_lower = vendor_id.lower()
            return self.VENDOR_ID_LOOKUP.get(vendor_id_lower, vendor_id)
        return vendor_id or "Unknown"
    
    def _format_device_display(self, device) -> str:
        """
        Format device information for display with vendor name.
        
        Args:
            device: USBDevice object with vendor_id and description attributes
        
        Returns:
            Formatted string with vendor name and device description
        """
        if not device:
            return "Unknown"
        
        vendor_name = self._get_vendor_name(device.vendor_id)
        device_desc = device.description or ""
        
        # If description is missing or is "Unknown device", use vendor name only
        # or provide a default description based on vendor
        if not device_desc or device_desc.lower() in ("unknown device", "unknown"):
            # Use vendor-specific defaults
            if vendor_name == "Elgato":
                device_desc = "Stream Deck"
            elif vendor_name == "Ketron":
                device_desc = "MIDI Device"
            elif vendor_name == "CH345":
                device_desc = "MIDI Adapter"
            elif vendor_name == "Adafruit":
                device_desc = "Device"
            else:
                # For unknown vendors, just show vendor name
                return vendor_name
        
        # Format: "Vendor Name - Device Description"
        return f"{vendor_name} - {device_desc}"
    
    def _update_usb_devices(self):
        """Update the displayed USB input and output devices, and refresh key mappings"""
        # Update UI to show we're scanning
        self.usb_input_label.config(text="Scanning...", foreground="gray")
        self.usb_output_label.config(text="Scanning...", foreground="gray")
        self.root.update_idletasks()  # Force UI update
        
        # First, refresh key mappings from key_mappings.json (same as on startup)
        try:
            # Find settings.yml file path (same logic as main())
            # control_panel.py is at: devdeck/gui/control_panel.py
            # Project root is 3 levels up: gui -> devdeck -> project_root
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / 'config'
            settings_filename = config_dir / 'settings.yml'
            
            if settings_filename.exists():
                # Update settings.yml from key_mappings.json
                updated = DevDeckSettings.update_from_key_mappings(str(settings_filename))
                if updated:
                    self.logger.info("Key mappings updated successfully from key_mappings.json")
                    # Reload key mappings in GUI for display
                    self._load_key_mappings()
                else:
                    self.logger.debug("Key mappings file not found or empty, skipping update")
            else:
                self.logger.warning(f"Settings file not found: {settings_filename}, skipping key mappings update")
        except Exception as e:
            # Log error but don't fail - continue with USB device refresh
            self.logger.warning(f"Error updating key mappings: {e}", exc_info=True)
        
        # Now refresh USB devices (existing functionality)
        try:
            # Check for Elgato Stream Deck (USB Input Device)
            elgato_connected, elgato_device = check_elgato_stream_deck()
            
            if elgato_connected:
                if elgato_device:
                    # Show vendor name and device description
                    device_text = self._format_device_display(elgato_device)
                    self.usb_input_label.config(text=device_text, foreground="green")
                else:
                    # Windows - device detected but no USB info available
                    # Use vendor lookup for Elgato (0fd9)
                    vendor_name = self._get_vendor_name('0fd9')
                    self.usb_input_label.config(text=f"{vendor_name} - Stream Deck (detected)", 
                                               foreground="green")
            else:
                self.usb_input_label.config(text="Not detected", 
                                           foreground="red")
            
            # Check for MIDI output USB device
            midi_connected, midi_device = check_midi_output_device()
            
            if midi_connected:
                if midi_device:
                    # Show vendor name and device description
                    device_text = self._format_device_display(midi_device)
                    self.usb_output_label.config(text=device_text, foreground="green")
                else:
                    # Windows - device detected but no USB info available
                    self.usb_output_label.config(text="MIDI Output Device (detected)", 
                                                foreground="green")
            else:
                self.usb_output_label.config(text="Not detected", 
                                            foreground="red")
                
        except Exception as e:
            # Catch any exceptions
            self.logger.error(f"Error updating USB devices: {e}", exc_info=True)
            self.usb_input_label.config(text="Error: Click to retry", 
                                       foreground="red")
            self.usb_output_label.config(text="Error: Click to retry", 
                                         foreground="red")
    
    def _start_midi_monitoring(self):
        """Start monitoring MIDI input"""
        if mido is None:
            self.logger.error("mido library not available for MIDI monitoring")
            return
        
        if self.midi_monitoring:
            return
        
        try:
            # Get input ports with safe wrapper for GIL safety
            input_ports = self._safe_midi_call(lambda: mido.get_input_names(), default=[])
            
            if not input_ports:
                self.logger.warning("No MIDI input ports available")
                return
            
            # Use the first available input port
            port_name = input_ports[0]
            self.midi_input_port = self._safe_midi_call(
                lambda: mido.open_input(port_name), 
                default=None
            )
            
            if self.midi_input_port is None:
                self.logger.error(f"Failed to open MIDI input port {port_name}")
                return
            
            self.midi_monitoring = True
            self.midi_stop_event.clear()
            
            def monitor_midi():
                """Thread function to monitor MIDI messages"""
                try:
                    for msg in self.midi_input_port:
                        if self.midi_stop_event.is_set():
                            break
                        
                        # Only log note on/off messages (key presses)
                        if msg.type in ('note_on', 'note_off'):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            if msg.type == 'note_on' and msg.velocity > 0:
                                key_info = f"[{timestamp}] Note ON: Note={msg.note}, Velocity={msg.velocity}, Channel={msg.channel + 1}"
                            else:
                                key_info = f"[{timestamp}] Note OFF: Note={msg.note}, Channel={msg.channel + 1}"
                            
                            self.midi_message_queue.put(key_info)
                except Exception as e:
                    if not self.midi_stop_event.is_set():
                        self.logger.error(f"Error in MIDI monitoring thread: {e}")
            
            self.midi_input_thread = threading.Thread(target=monitor_midi, daemon=True)
            self.midi_input_thread.start()
            
            self.logger.info(f"Started MIDI monitoring on port: {port_name}")
            
            # Add status message to monitor
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.midi_message_queue.put(f"[{timestamp}] EVM Deck application ready")
            
        except Exception as e:
            self.logger.error(f"Error starting MIDI monitoring: {e}")
            self.midi_monitoring = False
    
    def _stop_midi_monitoring(self):
        """Stop monitoring MIDI input"""
        if not self.midi_monitoring:
            return
        
        self.midi_monitoring = False
        self.midi_stop_event.set()
        
        if self.midi_input_port:
            try:
                self.midi_input_port.close()
            except Exception:
                pass
            self.midi_input_port = None
        
        self.logger.info("Stopped MIDI monitoring")
        
        # Add status message to monitor
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.midi_message_queue.put(f"[{timestamp}] MIDI monitoring stopped")
    
    def _load_key_mappings(self):
        """Load key mappings from key_mappings.json"""
        try:
            # Try to find key_mappings.json in config directory
            project_root = Path(__file__).parent.parent.parent
            key_mappings_file = project_root / 'config' / 'key_mappings.json'
            
            if not key_mappings_file.exists():
                key_mappings_file = project_root / 'key_mappings.json'
            
            if key_mappings_file.exists():
                with open(key_mappings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try UTF-16 first, then UTF-8
                try:
                    key_mappings_data = json.loads(content)
                except json.JSONDecodeError:
                    with open(key_mappings_file, 'r', encoding='utf-16') as f:
                        content = f.read()
                    key_mappings_data = json.loads(content)
                
                # Handle both named structure {"key_mappings": [...]} and direct array [...]
                if isinstance(key_mappings_data, dict) and 'key_mappings' in key_mappings_data:
                    key_mappings = key_mappings_data['key_mappings']
                elif isinstance(key_mappings_data, list):
                    key_mappings = key_mappings_data
                else:
                    key_mappings = []
                
                # Create mapping: key_no -> key_name
                self.key_mappings = {
                    mapping['key_no']: mapping.get('key_name', '').strip()
                    for mapping in key_mappings
                    if 'key_no' in mapping
                }
                self.logger.info(f"Loaded {len(self.key_mappings)} key mappings")
            else:
                self.logger.warning(f"Key mappings file not found: {key_mappings_file}")
        except Exception as e:
            self.logger.error(f"Error loading key mappings: {e}", exc_info=True)
    
    def _get_key_name(self, key_no: int) -> str:
        """Get key name from key number"""
        return self.key_mappings.get(key_no, f"Key {key_no}")
    
    def _process_midi_messages(self):
        """Process MIDI messages and Stream Deck key presses from queues and update the text widget"""
        try:
            # Process MIDI messages
            while True:
                try:
                    message = self.midi_message_queue.get_nowait()
                    self._add_midi_message(message)
                except queue.Empty:
                    break
            
            # Process Stream Deck key presses
            while True:
                try:
                    # Handle both old format (key_no, key_name) and new format (key_no, key_name, midi_hex)
                    item = self.streamdeck_key_queue.get_nowait()
                    if len(item) == 2:
                        key_no, key_name = item
                        midi_hex = None
                    else:
                        key_no, key_name, midi_hex = item
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Use provided key_name or look it up
                    if key_name:
                        display_name = key_name
                    else:
                        display_name = self._get_key_name(key_no)
                    
                    # Format message with MIDI hex if available (wrapped in square brackets)
                    if midi_hex:
                        key_info = f"[{timestamp}] Pressed {display_name} [{midi_hex}]"
                    else:
                        key_info = f"[{timestamp}] Pressed {display_name}"
                    self._add_midi_message(key_info)
                except queue.Empty:
                    break
        except Exception as e:
            self.logger.error(f"Error processing messages: {e}")
        
        # Schedule next check
        self.root.after(100, self._process_midi_messages)
    
    def _add_midi_message(self, message: str):
        """Add a MIDI message to the text widget"""
        self.midi_text.config(state=tk.NORMAL)
        
        # Insert new message at the end
        self.midi_text.insert(tk.END, message + "\n")
        
        # Keep only the last ~50 lines (approximately 3 visible rows worth)
        lines = self.midi_text.get("1.0", tk.END).split("\n")
        if len(lines) > 50:
            self.midi_text.delete("1.0", f"{len(lines) - 50}.0")
        
        # Scroll to bottom
        self.midi_text.see(tk.END)
        self.midi_text.config(state=tk.DISABLED)
    
    def _on_closing(self):
        """Handle window close event"""
        self._stop_midi_monitoring()
        
        # Clear the screen BEFORE stopping the application (while deck is still open)
        # This ensures we can clear it even if the app thread doesn't exit cleanly
        if self.app_running:
            self.logger.info("Application is running, clearing screen before stopping...")
            self._clear_stream_deck_screen_while_open()
        
        # Stop the application - this will also clear the screen via DeckManager.close()
        # but we've already cleared it above as a safety measure
        self._stop_application()
        
        # Try to clear screen as final fallback (in case app wasn't running or clear failed)
        if not self.app_running:
            self._clear_stream_deck_screen()
        
        self.root.destroy()
    
    def _clear_stream_deck_screen_while_open(self):
        """
        Clear the Stream Deck screen while the application is still running.
        
        This uses the registered DeckManager to clear the screen using the
        already-open deck.
        """
        try:
            self.logger.info("Attempting to clear Stream Deck screen (deck should be open)...")
            
            # Try to get the registered DeckManager
            if _DECK_MANAGER_REGISTRY_AVAILABLE and get_deck_manager:
                deck_manager = get_deck_manager()
                if deck_manager:
                    try:
                        deck_manager.clear_screen()
                        self.logger.info("Stream Deck screen cleared successfully via DeckManager")
                        return
                    except Exception as ex:
                        self.logger.warning("Error clearing screen via DeckManager: %s", ex)
            
            # Fallback: try to access deck directly via DeviceManager
            self.logger.debug("DeckManager not available, trying direct access...")
            streamdecks = DeviceManager().enumerate()
            
            if not streamdecks:
                self.logger.debug("No Stream Deck detected for screen clear")
                return
            
            # Try to clear each detected deck
            for deck in streamdecks:
                try:
                    # Try to use the deck directly (it should be open)
                    try:
                        keys = deck.key_count()
                        
                        # Create a minimal deck manager-like object for DeckContext
                        class MinimalDeckManager:
                            def __init__(self, deck):
                                self.decks = []
                                self._deck = deck
                        
                        minimal_manager = MinimalDeckManager(deck)
                        context = DeckContext(minimal_manager, deck)
                        
                        # Clear all keys to black
                        for key_no in range(keys):
                            with context.renderer(key_no) as r:
                                r.background_color('black')
                                r.text('')\
                                    .font_size(100)\
                                    .color('black')\
                                    .center_vertically()\
                                    .center_horizontally()\
                                    .end()
                        
                        self.logger.info("Stream Deck screen cleared successfully (direct access)")
                        return
                    except Exception as ex:
                        self.logger.debug(f"Could not access deck directly: {ex}")
                        # Can't access the open deck, that's okay - DeckManager.close() will handle it
                except Exception as ex:
                    self.logger.warning("Error clearing Stream Deck screen while open: %s", ex)
        except Exception as ex:
            self.logger.warning("Failed to clear Stream Deck screen while open: %s", ex)
    
    def _send_start_stop(self):
        """
        Send Start/Stop MIDI SysEx message to the USB output device.
        
        Reuses the same logic as the Elgato Start/Stop button.
        """
        try:
            self.logger.info("Start/Stop button pressed in GUI")
            
            # Get MIDI port name from MidiManager
            port_name = None
            try:
                # Use lazy-initialized midi_manager
                midi_mgr = self.midi_manager
                
                # Get open ports
                open_ports = midi_mgr.get_open_ports()
                if open_ports:
                    port_name = open_ports[0]
                    self.logger.info(f"Using open MIDI port: {port_name}")
                else:
                    # Try to auto-connect to hardware port
                    self.logger.debug("No open ports, attempting to auto-connect...")
                    if midi_mgr.auto_connect_hardware_port():
                        open_ports = midi_mgr.get_open_ports()
                        if open_ports:
                            port_name = open_ports[0]
                            self.logger.info(f"Auto-connected to MIDI port: {port_name}")
                        else:
                            self.logger.warning("Auto-connect reported success but no ports are open")
                    else:
                        self.logger.warning("Failed to auto-connect to MIDI hardware port")
            except Exception as e:
                self.logger.warning(f"Error getting MIDI port: {e}", exc_info=True)
            
            # Create KetronMidi instance and send Start/Stop command
            ketron_midi = KetronMidi()
            success = ketron_midi.send_pedal_command("Start/Stop", port_name)
            
            if success:
                self.logger.info("Start/Stop MIDI command sent successfully")
            else:
                self.logger.error("Failed to send Start/Stop MIDI command")
                
        except Exception as e:
            self.logger.error(f"Error sending Start/Stop command: {e}", exc_info=True)
    
    def _clear_stream_deck_screen(self):
        """
        Clear the Stream Deck screen by setting all keys to black.
        
        This is called when the GUI exits to provide a clean shutdown.
        """
        try:
            self.logger.info("Clearing Stream Deck screen on exit...")
            
            # Wait a short moment for the device to be released after stopping the application
            # This helps avoid "No HID device" errors
            time.sleep(0.5)
            
            # Access Stream Deck using DeviceManager (similar to main())
            streamdecks = DeviceManager().enumerate()
            
            if not streamdecks:
                self.logger.debug("No Stream Deck detected for screen clear")
                return
            
            # Clear each detected deck with retry logic
            for deck in streamdecks:
                deck_opened = False
                max_retries = 3
                retry_delay = 0.3
                
                for attempt in range(max_retries):
                    try:
                        # Try to open the deck
                        try:
                            deck.open()
                            deck_opened = True
                        except Exception as open_ex:
                            error_msg = str(open_ex).lower()
                            if "hid device" in error_msg or "could not open" in error_msg:
                                if attempt < max_retries - 1:
                                    # Wait and retry
                                    self.logger.debug(f"Device not ready, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})...")
                                    time.sleep(retry_delay)
                                    continue
                                else:
                                    # Last attempt failed, log and skip
                                    self.logger.warning(f"Could not open Stream Deck after {max_retries} attempts: {open_ex}")
                                    return
                            else:
                                # Different error, might be already open, try to use it anyway
                                self.logger.debug("Deck might already be open, attempting to clear anyway")
                        
                        # Create a minimal deck manager-like object for DeckContext
                        # We only need the deck reference, not a full DeckManager
                        class MinimalDeckManager:
                            def __init__(self, deck):
                                self.decks = []
                                self._deck = deck
                        
                        minimal_manager = MinimalDeckManager(deck)
                        context = DeckContext(minimal_manager, deck)
                        
                        # Clear all keys to black
                        keys = deck.key_count()
                        for key_no in range(keys):
                            with context.renderer(key_no) as r:
                                r.background_color('black')
                                r.text('')\
                                    .font_size(100)\
                                    .color('black')\
                                    .center_vertically()\
                                    .center_horizontally()\
                                    .end()
                        
                        self.logger.info("Stream Deck screen cleared successfully")
                        
                        # Close the deck only if we opened it
                        if deck_opened:
                            deck.close()
                        
                        # Success, break out of retry loop
                        break
                        
                    except Exception as ex:
                        error_msg = str(ex).lower()
                        if ("hid device" in error_msg or "could not open" in error_msg) and attempt < max_retries - 1:
                            # Retry on HID device errors
                            self.logger.debug(f"Error accessing device, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            # Other error or last attempt
                            self.logger.warning("Error clearing Stream Deck screen: %s", ex, exc_info=True)
                            # Try to close the deck even if clearing failed (only if we opened it)
                            if deck_opened:
                                try:
                                    deck.close()
                                except Exception:
                                    pass  # Ignore errors when closing
                            # If it's not a retryable error, break
                            if "hid device" not in error_msg and "could not open" not in error_msg:
                                break
                            
        except Exception as ex:
            # Don't block GUI exit if screen clearing fails
            self.logger.warning("Failed to clear Stream Deck screen: %s", ex, exc_info=True)


def run_gui():
    """Run the GUI control panel"""
    import sys
    logger = logging.getLogger('devdeck')
    
    try:
        logger.info("Initializing GUI...")
        root = tk.Tk()
        logger.info("Creating control panel...")
        app = DevDeckControlPanel(root)
        logger.info("GUI initialized, starting main loop...")
        # Start the main loop - this blocks until window is closed
        root.mainloop()
        logger.info("GUI main loop exited")
    except KeyboardInterrupt:
        logger.info("GUI interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error starting GUI: {e}", exc_info=True)
        print(f"Fatal error starting GUI: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_gui()

