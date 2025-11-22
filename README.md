# Dev Deck
![CI](https://github.com/jamesridgway/devdeck/workflows/CI/badge.svg?branch=main)

Stream Deck control software for software developer's.

[![DevDeck Demo](https://files.jamesridgway.co.uk/images/streamdeck-yt-thumbnail.png)](https://www.youtube.com/watch?v=4ZvrVFW562w)

## Getting Started

If this is your fist time using a StreamDeck make sure to follow the [Pre-requisite: LibUSB HIDAPI Backend](https://github.com/jamesridgway/devdeck/wiki/Installation#pre-requisite-libusb-hidapi-backend) steps documented in the wiki

Install DevDeck

    pip install devdeck


You should then be able to run DevDeck by running:

    devdeck

The first time that DevDeck is run, it will generate a basic `~/.devdeck/settings.yml` populated with the clock control for any Stream Decks that are connected.


## Built-in Controls
Dev Deck ships with the following controls:

* [Clock Control](https://github.com/jamesridgway/devdeck/wiki/Controls#clock-control)
  
  `devdeck.controls.clock_control.ClockControl` is a clock widget for displaying the date and time

* [Command Execution](https://github.com/jamesridgway/devdeck/wiki/Controls#command-control)
  
  `devdeck.controls.command_control.CommandControl` is a control for executing commands on your computer. You can
   specify any command and icon for the given action.

* [Microphone Mute Toggle](https://github.com/jamesridgway/devdeck/wiki/Controls#mic-mute-control)

  `devdeck.controls.mic_mute_control.MicMuteControl` toggles the mute on a given microphone input.

* [Name List](https://github.com/jamesridgway/devdeck/wiki/Controls#name-list-control)

  `devdeck.controls.name_list_control.NameListControl` cycles through initials from a list of names. Useful for things
  like stand-ups were you need to rotate through a team and make sure you cover everyone.
  
* [Timer](https://github.com/jamesridgway/devdeck/wiki/Controls#timer-control)
  
  `devdeck.controls.timer_control.TimerControl` a basic stopwatch timer that can be used to start/stop/reset timing.

* [Volume Control](https://github.com/jamesridgway/devdeck/wiki/Controls#volume-level-control)

  `devdeck.controls.volume_level_control.VolumeLevelControl` sets the volume for a given output to a specified volume 
  level.


* [Volume Mute Control](https://github.com/jamesridgway/devdeck/wiki/Controls#volume-mute-control)

  `devdeck.controls.volume_mute_control.VolumeMuteControl` toggles the muting of a given output.


## Built-in Decks

* [Single Page Deck](https://github.com/jamesridgway/devdeck/wiki/Decks#singlepagedeckcontroller)

  `devdeck.decks.single_page_deck_controller.SinglePageDeckController` provides a basic single page deck for
  controls to be arranged on.

* [Volume Deck](https://github.com/jamesridgway/devdeck/wiki/Decks#volumedeck)

  `devdeck.decks.volume_deck.VolumeDeck` is a pre-built volume deck which will show volume toggles between 0% and 100%
  at 10% increments.

## Plugins
There are a few controls that are provided as plugins. You can always write your own plugin if you can't find the
functionality that you're after:

* [devdeck-slack](https://github.com/jamesridgway/devdeck-slack)

  Controls and decks for Slack. Toggle presence, change status, snooze notifications, etc.

* [devdeck-home-assistant](https://github.com/jamesridgway/devdeck-home-assistant)

  Controls and decks for Home Assistant. Toggle lights, switches, etc.

* [devdeck-key-light](https://github.com/jamesridgway/devdeck-key-light)

  Controls and decks for controlling an Elgato Key Light.

## Implementing Custom Controls
Can't find support for what you want? Implement your own `DeckControl` or `DeckController`·

* `DeckControl`
  
  A `DeckControl` is an individual button that can be placed on a deck.
  
* `DeckController`

  A `DeckController` is fronted by a button, pressing the button will take you to a deck screen tailored for the
  given functionality.
  
  For example: Slack is implemented as a DeckController. Pressing the slack button will then present you with buttons
  for specific statuses.
 
 ## Developing for DevDeck
 Pull requests and contributions to this project are welcome.
 
 You can get setup with a virtual environment and all necessary dependencies by running:
 
    ./setup.sh
    
Tests can be run by running:

    ./run-tests.sh

## Known Issues & Fixes

### Clock Control Compatibility with Pillow 10.0.0+

**Issue**: The clock control may fail with `AttributeError: 'ImageDraw' object has no attribute 'textsize'` when using Pillow 10.0.0 or later.

**Cause**: The `devdeck-core` package uses the deprecated `textsize()` method which was removed in Pillow 10.0.0.

**Fix**: Update `text_renderer.py` in the installed `devdeck-core` package to use `textbbox()` instead of `textsize()`. The fix is located at:
- `venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py`

Replace:
```python
label_w, label_h = draw.textsize('%s' % self.text, font=font)
```

With:
```python
# textsize() was deprecated and removed in Pillow 10.0.0, use textbbox() instead
bbox = draw.textbbox((0, 0), '%s' % self.text, font=font)
label_w = bbox[2] - bbox[0]  # right - left
label_h = bbox[3] - bbox[1]  # bottom - top
```

**Note**: This fix is applied to your local virtual environment. If you recreate the venv or reinstall `devdeck-core`, you'll need to reapply this fix. Consider submitting a patch to the `devdeck-core` project for a permanent solution.

### Python 3.10+ Deprecation Warning

**Issue**: A deprecation warning about `threading.currentThread()` when running on Python 3.10+.

**Fix**: Updated `devdeck/main.py` to use `threading.current_thread()` instead of the deprecated `threading.currentThread()`.

### Windows: HIDAPI DLL Not Found

**Issue**: On Windows, you may encounter `ProbeError: No suitable LibUSB HIDAPI library found on this system. Is the 'hidapi.dll' library installed?` even when `hidapi.dll` is in your PATH.

**Cause**: Python's ctypes library looks for DLLs in specific locations, and the StreamDeck library may not find `hidapi.dll` even if it's in the system PATH.

**Fix**: Copy `hidapi.dll` to your Python Scripts directory (where `python.exe` is located). For a virtual environment:

```powershell
Copy-Item "C:\hidapi-win\x64\hidapi.dll" -Destination "venv\Scripts\hidapi.dll" -Force
```

Or if using a system Python installation:

```powershell
Copy-Item "C:\hidapi-win\x64\hidapi.dll" -Destination "$env:USERPROFILE\AppData\Local\Programs\Python\Python313\Scripts\hidapi.dll" -Force
```

**Alternative**: Ensure `C:\hidapi-win\x64` (or wherever your `hidapi.dll` is located) is permanently added to your system PATH environment variable, then restart your terminal/IDE.

### Stream Deck Application Conflict

**Issue**: Factory default images appear on keys, factory actions are triggered when pressing keys, or devdeck controls don't work as expected.

**Cause**: The official Stream Deck application is still running in the background and controlling the device. The Stream Deck can only be controlled by one application at a time.

**Fix**: Close the official Stream Deck application completely before running devdeck:

1. **Close the Stream Deck application**: Exit the Stream Deck app from the system tray or taskbar
2. **Check for background processes**: Ensure no Stream Deck processes are running in the background
3. **Restart devdeck**: After closing the official app, restart devdeck

**Note**: You cannot use both the official Stream Deck application and devdeck simultaneously. Only one application can control the Stream Deck at a time.

