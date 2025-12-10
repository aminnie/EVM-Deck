"""
GUI Control Panel for DevDeck Application

Provides a simple GUI interface to:
- Control application start, stop, and restart
- Monitor MIDI key presses
- Display connected MIDI input and output devices
"""

import logging
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, List
from datetime import datetime

try:
    import mido
except ImportError:
    mido = None

from devdeck.midi import MidiManager


class DevDeckControlPanel:
    """Main GUI control panel for DevDeck application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DevDeck Control Panel")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        self.logger = logging.getLogger('devdeck')
        
        # Application control state
        self.app_thread: Optional[threading.Thread] = None
        self.app_running = False
        self.app_stop_event = threading.Event()
        
        # MIDI monitoring state
        self.midi_input_thread: Optional[threading.Thread] = None
        self.midi_input_port = None
        self.midi_monitoring = False
        self.midi_stop_event = threading.Event()
        self.midi_message_queue = queue.Queue()
        
        # MIDI manager
        self.midi_manager = MidiManager()
        
        # Build UI
        self._build_ui()
        
        # Start MIDI device monitoring
        self._update_midi_devices()
        
        # Start MIDI message processing
        self._process_midi_messages()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _build_ui(self):
        """Build the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DevDeck Control Panel", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Application Control Section
        control_frame = ttk.LabelFrame(main_frame, text="Application Control", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text="Start", 
                                       command=self._start_application, width=12)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self._stop_application, width=12,
                                     state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.restart_button = ttk.Button(button_frame, text="Restart", 
                                         command=self._restart_application, width=12,
                                         state=tk.DISABLED)
        self.restart_button.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", 
                                      foreground="red")
        self.status_label.grid(row=1, column=0, pady=(10, 0))
        
        # MIDI Devices Section
        devices_frame = ttk.LabelFrame(main_frame, text="MIDI Devices", padding="10")
        devices_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        devices_frame.columnconfigure(0, weight=1)
        
        # MIDI Input
        ttk.Label(devices_frame, text="MIDI Input:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.midi_input_label = ttk.Label(devices_frame, text="None", 
                                          foreground="gray")
        self.midi_input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # MIDI Output
        ttk.Label(devices_frame, text="MIDI Output:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.midi_output_label = ttk.Label(devices_frame, text="None", 
                                           foreground="gray")
        self.midi_output_label.grid(row=3, column=0, sticky=tk.W)
        
        # Refresh button
        refresh_button = ttk.Button(devices_frame, text="Refresh Devices", 
                                    command=self._update_midi_devices)
        refresh_button.grid(row=4, column=0, pady=(10, 0))
        
        # MIDI Key Monitor Section
        monitor_frame = ttk.LabelFrame(main_frame, text="MIDI Key Press Monitor", padding="10")
        monitor_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Scrolled text for MIDI messages (3 rows visible)
        self.midi_text = scrolledtext.ScrolledText(monitor_frame, height=3, 
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.midi_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Start MIDI monitoring button
        self.midi_monitor_button = ttk.Button(monitor_frame, text="Start MIDI Monitor", 
                                              command=self._toggle_midi_monitoring)
        self.midi_monitor_button.grid(row=1, column=0, pady=(10, 0))
    
    def _start_application(self):
        """Start the DevDeck application in a separate thread"""
        if self.app_running:
            return
        
        self.app_running = True
        self.app_stop_event.clear()
        
        def run_app():
            try:
                # Import here to avoid circular import
                from devdeck.main import main as devdeck_main
                # Note: This will run the main() function
                # We may need to modify main() to check for stop events
                devdeck_main()
            except Exception as e:
                self.logger.error(f"Error in application thread: {e}", exc_info=True)
                self.root.after(0, lambda: self._update_status("Error", "red"))
            finally:
                self.app_running = False
                self.root.after(0, lambda: self._update_status("Stopped", "red"))
                self.root.after(0, self._update_buttons)
        
        self.app_thread = threading.Thread(target=run_app, daemon=True)
        self.app_thread.start()
        
        self._update_status("Running", "green")
        self._update_buttons()
    
    def _stop_application(self):
        """Stop the DevDeck application"""
        if not self.app_running:
            return
        
        # Set stop event (application would need to check this)
        self.app_stop_event.set()
        
        # Note: The main() function doesn't currently support graceful shutdown
        # You may need to modify it to check for stop events or use process termination
        # For now, we'll just update the UI state
        self.app_running = False
        self._update_status("Stopping...", "orange")
        self._update_buttons()
        
        # Wait a bit for thread to finish (non-blocking)
        def check_thread():
            if self.app_thread and self.app_thread.is_alive():
                self.root.after(100, check_thread)
            else:
                self._update_status("Stopped", "red")
                self._update_buttons()
        
        self.root.after(100, check_thread)
    
    def _restart_application(self):
        """Restart the DevDeck application"""
        self._stop_application()
        
        def start_after_stop():
            if not self.app_running:
                self._start_application()
        
        self.root.after(500, start_after_stop)
    
    def _update_status(self, status: str, color: str):
        """Update the status label"""
        self.status_label.config(text=f"Status: {status}", foreground=color)
    
    def _update_buttons(self):
        """Update button states based on application state"""
        if self.app_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
    
    def _update_midi_devices(self):
        """Update the displayed MIDI input and output devices"""
        if mido is None:
            self.midi_input_label.config(text="MIDI library not available", 
                                        foreground="red")
            self.midi_output_label.config(text="MIDI library not available", 
                                         foreground="red")
            return
        
        try:
            # Get MIDI input ports
            input_ports = mido.get_input_names()
            if input_ports:
                # Show all input ports, or first one if only one
                if len(input_ports) == 1:
                    input_text = input_ports[0]
                else:
                    input_text = f"{len(input_ports)} devices: {', '.join(input_ports[:3])}"
                    if len(input_ports) > 3:
                        input_text += "..."
                self.midi_input_label.config(text=input_text, foreground="black")
            else:
                self.midi_input_label.config(text="No MIDI input devices", 
                                           foreground="gray")
            
            # Get MIDI output ports
            output_ports = mido.get_output_names()
            open_ports = self.midi_manager.get_open_ports()
            
            if open_ports:
                # Show the currently open port(s)
                if len(open_ports) == 1:
                    output_text = open_ports[0]
                else:
                    output_text = f"{len(open_ports)} open: {', '.join(open_ports[:2])}"
                    if len(open_ports) > 2:
                        output_text += "..."
                self.midi_output_label.config(text=output_text, foreground="green")
            elif output_ports:
                # Show available ports if none are open
                if len(output_ports) == 1:
                    output_text = output_ports[0]
                else:
                    output_text = f"{len(output_ports)} available: {', '.join(output_ports[:2])}"
                    if len(output_ports) > 2:
                        output_text += "..."
                self.midi_output_label.config(text=output_text, foreground="orange")
            else:
                self.midi_output_label.config(text="No MIDI output devices", 
                                             foreground="gray")
        except Exception as e:
            self.logger.error(f"Error updating MIDI devices: {e}")
            self.midi_input_label.config(text="Error reading devices", 
                                       foreground="red")
            self.midi_output_label.config(text="Error reading devices", 
                                         foreground="red")
    
    def _toggle_midi_monitoring(self):
        """Start or stop MIDI input monitoring"""
        if self.midi_monitoring:
            self._stop_midi_monitoring()
        else:
            self._start_midi_monitoring()
    
    def _start_midi_monitoring(self):
        """Start monitoring MIDI input"""
        if mido is None:
            self.logger.error("mido library not available for MIDI monitoring")
            return
        
        if self.midi_monitoring:
            return
        
        try:
            input_ports = mido.get_input_names()
            if not input_ports:
                self.logger.warning("No MIDI input ports available")
                return
            
            # Use the first available input port
            port_name = input_ports[0]
            self.midi_input_port = mido.open_input(port_name)
            
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
            
            self.midi_monitor_button.config(text="Stop MIDI Monitor")
            self.logger.info(f"Started MIDI monitoring on port: {port_name}")
            
            # Add status message to monitor
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.midi_message_queue.put(f"[{timestamp}] MIDI monitoring started on: {port_name}")
            
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
        
        self.midi_monitor_button.config(text="Start MIDI Monitor")
        self.logger.info("Stopped MIDI monitoring")
        
        # Add status message to monitor
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.midi_message_queue.put(f"[{timestamp}] MIDI monitoring stopped")
    
    def _process_midi_messages(self):
        """Process MIDI messages from the queue and update the text widget"""
        try:
            while True:
                try:
                    message = self.midi_message_queue.get_nowait()
                    self._add_midi_message(message)
                except queue.Empty:
                    break
        except Exception as e:
            self.logger.error(f"Error processing MIDI messages: {e}")
        
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
        self._stop_application()
        self.root.destroy()


def run_gui():
    """Run the GUI control panel"""
    root = tk.Tk()
    app = DevDeckControlPanel(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()

