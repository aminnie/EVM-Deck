import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from StreamDeck.DeviceManager import DeviceManager

from devdeck.deck_manager import DeckManager
from devdeck.filters import InfoFilter
from devdeck.midi import MidiManager
from devdeck.settings.devdeck_settings import DevDeckSettings
from devdeck.settings.migration import SettingsMigrator
from devdeck.settings.validation_error import ValidationError
from devdeck.usb_device_checker import check_elgato_stream_deck, check_midi_output_device


def main() -> None:
    # Use pathlib consistently for path handling
    devdeck_dir = Path.home() / 'devdeck'
    devdeck_dir.mkdir(exist_ok=True)

    root = logging.getLogger('devdeck')
    root.setLevel(logging.DEBUG)

    # Formatter with milliseconds (default %(asctime)s includes milliseconds: YYYY-MM-DD HH:MM:SS,mmm)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(InfoFilter())
    root.addHandler(info_handler)

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)

    # Get project root and create logs directory
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / 'devdeck.log'
    fileHandler = RotatingFileHandler(str(log_file), maxBytes=100000, backupCount=5)
    fileHandler.setFormatter(formatter)
    root.addHandler(fileHandler)

    # Validate required USB devices before proceeding
    root.info("Checking for required USB devices...")
    
    # Check for Elgato Stream Deck
    elgato_connected, elgato_device = check_elgato_stream_deck()
    if not elgato_connected:
        root.error("=" * 60)
        root.error("ERROR: Elgato Stream Deck not detected!")
        root.error("=" * 60)
        root.error("Please ensure your Elgato Stream Deck is connected via USB.")
        root.error("On Linux/Raspberry Pi, verify with: lsusb | grep -i elgato")
        root.error("=" * 60)
        print("\n" + "=" * 60)
        print("ERROR: Elgato Stream Deck not detected!")
        print("=" * 60)
        print("Please ensure your Elgato Stream Deck is connected via USB.")
        print("On Linux/Raspberry Pi, verify with: lsusb | grep -i elgato")
        print("=" * 60 + "\n")
        sys.exit(1)
    else:
        if elgato_device:
            root.info(f"Elgato Stream Deck USB connection: {elgato_device.description} "
                     f"(Bus {elgato_device.bus}, Device {elgato_device.device}, "
                     f"ID {elgato_device.vendor_id}:{elgato_device.product_id})")
        else:
            root.info("Elgato Stream Deck detection passed (Windows - using library detection)")
    
    # Check for MIDI output USB device
    midi_connected, midi_device = check_midi_output_device()
    if not midi_connected:
        root.error("=" * 60)
        root.error("ERROR: MIDI output USB device not detected!")
        root.error("=" * 60)
        root.error("Please ensure a MIDI output USB device is connected.")
        root.error("On Linux/Raspberry Pi, verify with: lsusb | grep -i midi")
        root.error("=" * 60)
        print("\n" + "=" * 60)
        print("ERROR: MIDI output USB device not detected!")
        print("=" * 60)
        print("Please ensure a MIDI output USB device is connected.")
        print("On Linux/Raspberry Pi, verify with: lsusb | grep -i midi")
        print("=" * 60 + "\n")
        sys.exit(1)
    else:
        if midi_device:
            root.info(f"MIDI output USB device detected: {midi_device.description} "
                     f"(Bus {midi_device.bus}, Device {midi_device.device}, "
                     f"ID {midi_device.vendor_id}:{midi_device.product_id})")
        else:
            root.info("MIDI device detection passed (Windows - using port enumeration)")
    
    # Automatically connect to MIDI hardware port
    root.info("Initializing MIDI manager and auto-connecting to hardware port...")
    midi_manager = MidiManager()
    if midi_manager.auto_connect_hardware_port():
        open_ports = midi_manager.get_open_ports()
        if open_ports:
            selected_port = open_ports[0]
            root.info(f"Selected MIDI USB port: {selected_port}")
            # Try to match the MIDI port with the USB device for additional details
            if midi_device:
                root.info(f"MIDI port '{selected_port}' corresponds to USB device: "
                         f"{midi_device.description} (Bus {midi_device.bus}, Device {midi_device.device})")
        else:
            root.warning("MIDI port connection reported success but no ports are open")
    else:
        root.error("=" * 60)
        root.error("ERROR: Failed to connect to MIDI hardware port!")
        root.error("=" * 60)
        root.error("Please ensure a MIDI output device is connected and accessible.")
        root.error("Available MIDI ports can be checked with: python -m devdeck.midi.midi_manager")
        root.error("=" * 60)
        print("\n" + "=" * 60)
        print("ERROR: Failed to connect to MIDI hardware port!")
        print("=" * 60)
        print("Please ensure a MIDI output device is connected and accessible.")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    root.info("Device validation complete. Proceeding with Stream Deck initialization...")

    streamdecks = DeviceManager().enumerate()

    # Get project root (parent of devdeck directory)
    project_root = Path(__file__).parent.parent
    config_dir = project_root / 'config'
    settings_filename = config_dir / 'settings.yml'
    
    # Migrate settings from old locations if needed
    SettingsMigrator.migrate_settings(project_root, config_dir, settings_filename)
    
    if not settings_filename.exists():
        root.warning("No settings file detected!")

        serial_numbers = []
        for index, deck in enumerate(streamdecks):
            deck.open()
            serial_numbers.append(deck.get_serial_number())
            deck.close()
        if len(serial_numbers) > 0:
            root.info("Generating a setting file as none exist: %s", settings_filename)
            DevDeckSettings.generate_default(str(settings_filename), serial_numbers)
        else:
            root.info("""No stream deck connected. Please connect a stream deck to generate an initial config file. \n
                         If you are having difficulty detecting your stream deck please follow the installation
                         instructions: https://github.com/jamesridgway/devdeck/wiki/Installation""")
            exit(0)

    # Update settings from key_mappings.json if it exists
    DevDeckSettings.update_from_key_mappings(str(settings_filename))
    
    try:
        settings = DevDeckSettings.load(str(settings_filename))
    except ValidationError as validation_error:
        root.error("Settings validation failed: %s", validation_error)
        print(validation_error)
        sys.exit(1)

    for index, deck in enumerate(streamdecks):
        deck.open()
        root.info('Connecting to deck: %s (S/N: %s)', deck.id(), deck.get_serial_number())

        deck_settings = settings.deck(deck.get_serial_number())
        if deck_settings is None:
            root.info("Skipping deck %s (S/N: %s) - no settings present", deck.id(), deck.get_serial_number())
            deck.close()
            continue

        # Get screen saver timeout from settings (optional, defaults to 15 seconds)
        deck_settings_dict = deck_settings.settings()
        screen_saver_timeout = deck_settings_dict.get('screen_saver_timeout')
        
        deck_manager = DeckManager(deck, screen_saver_timeout=screen_saver_timeout)

        # Instantiate deck
        main_deck = deck_settings.deck_class()(None, **deck_settings.settings())
        deck_manager.set_active_deck(main_deck)

        for t in threading.enumerate():
            if t is threading.current_thread():
                continue

            if t.is_alive():
                try:
                    t.join()
                except KeyboardInterrupt as ex:
                    deck_manager.close()
                    deck.close()

    if len(streamdecks) == 0:
        root.info("No streamdecks detected, exiting.")


if __name__ == '__main__':
    main()
