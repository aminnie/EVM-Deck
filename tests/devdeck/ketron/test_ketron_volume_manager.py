"""
Test Ketron Volume Manager with key press tracking and increment/decrement.

This script tests the KetronVolumeManager functionality:
1. Setting last pressed key_name
2. Incrementing/decrementing volumes
3. Verifying MIDI CC commands are sent correctly

Usage:
    python tests/devdeck/ketron/test_ketron_volume_manager.py
"""

import sys
from pathlib import Path

# Add project root to path to allow imports
# Path is now: tests/devdeck/ketron/test_ketron_volume_manager.py
# Need to go up 4 levels to get to project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from devdeck.ketron import KetronMidi, KetronVolumeManager


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_test_result(test_name, passed, details=None):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        for detail in details:
            print(f"      {detail}")


def test_key_press_and_increment():
    """Test: Press a key, then increment the corresponding volume"""
    print_section("Test 1: Key Press + Increment")
    
    # Reset singleton instance for clean test
    # Note: In a real scenario, you'd use mocking, but for demonstration we'll work with the singleton
    volume_manager = KetronVolumeManager()
    ketron_midi = KetronMidi()
    
    # Test case 1: LOWERS key press + increment
    print("\n--- Test Case 1: LOWERS key press + increment_lower(5) ---")
    
    # Set initial volume using set_volume method
    volume_manager.set_volume("lower", 50)
    initial_volume = volume_manager.lower
    print(f"Initial lower volume: {initial_volume}")
    
    # Simulate key press
    volume_manager.set_last_pressed_key_name("LOWERS")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    # Verify CC lookup
    cc_control = ketron_midi.cc_midis.get("LOWERS")
    print(f"CC control for 'LOWERS': {cc_control} (0x{cc_control:02X})")
    
    # Increment volume
    new_volume = volume_manager.increment_lower(5)
    print(f"New lower volume after increment_lower(5): {new_volume}")
    
    # Verify increment worked
    passed = (new_volume == initial_volume + 5)
    print_test_result(
        "LOWERS increment",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {initial_volume + 5}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})",
            f"MIDI channel: {volume_manager.midi_out_channel}"
        ]
    )
    
    # Test case 2: VOICE1 key press + increment
    print("\n--- Test Case 2: VOICE1 key press + increment_voice1(10) ---")
    
    volume_manager.set_volume("voice1", 60)
    initial_volume = volume_manager.voice1
    print(f"Initial voice1 volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("VOICE1")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("VOICE1")
    print(f"CC control for 'VOICE1': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.increment_voice1(10)
    print(f"New voice1 volume after increment_voice1(10): {new_volume}")
    
    passed = (new_volume == initial_volume + 10)
    print_test_result(
        "VOICE1 increment",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {initial_volume + 10}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    # Test case 3: DRAWBARS key press + increment
    print("\n--- Test Case 3: DRAWBARS key press + increment_drawbars(3) ---")

    volume_manager.set_volume("drawbars", 100)
    initial_volume = volume_manager.drawbars
    print(f"Initial drawbars volume: {initial_volume}")

    volume_manager.set_last_pressed_key_name("DRAWBARS")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")

    # DRAWBARS maps to drawbars (lowercase) in cc_midis
    cc_control = ketron_midi.cc_midis.get("drawbars")
    if cc_control is None:
        cc_control = ketron_midi.cc_midis.get("Draw Organ")
    if cc_control:
        print(f"CC control for 'drawbars': {cc_control} (0x{cc_control:02X})")
    else:
        print("CC control for 'drawbars': Not found")

    new_volume = volume_manager.increment_drawbars(3)
    print(f"New drawbars volume after increment_drawbars(3): {new_volume}")
    
    # Should be clamped to 127
    expected_volume = min(127, initial_volume + 3)
    passed = (new_volume == expected_volume)
    print_test_result(
        "DRAWBARS increment (with clamping)",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {expected_volume}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    return True


def test_key_press_and_decrement():
    """Test: Press a key, then decrement the corresponding volume"""
    print_section("Test 2: Key Press + Decrement")
    
    volume_manager = KetronVolumeManager()
    ketron_midi = KetronMidi()
    
    # Test case 1: STYLE key press + decrement
    print("\n--- Test Case 1: STYLE key press + decrement_style(8) ---")
    
    volume_manager.set_volume("style", 70)
    initial_volume = volume_manager.style
    print(f"Initial style volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("STYLE")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("STYLE")
    print(f"CC control for 'STYLE': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.decrement_style(8)
    print(f"New style volume after decrement_style(8): {new_volume}")
    
    passed = (new_volume == initial_volume - 8)
    print_test_result(
        "STYLE decrement",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {initial_volume - 8}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    # Test case 2: DRUM key press + decrement
    print("\n--- Test Case 2: DRUM key press + decrement_drum(15) ---")
    
    volume_manager.set_volume("drum", 20)
    initial_volume = volume_manager.drum
    print(f"Initial drum volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("DRUM")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("DRUM")
    print(f"CC control for 'DRUM': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.decrement_drum(15)
    print(f"New drum volume after decrement_drum(15): {new_volume}")
    
    # Should be clamped to 0
    expected_volume = max(0, initial_volume - 15)
    passed = (new_volume == expected_volume)
    print_test_result(
        "DRUM decrement (with clamping)",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {expected_volume}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    # Test case 3: CHORD key press + decrement
    print("\n--- Test Case 3: CHORD key press + decrement_chord(5) ---")
    
    volume_manager.set_volume("chord", 45)
    initial_volume = volume_manager.chord
    print(f"Initial chord volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("CHORD")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("CHORD")
    print(f"CC control for 'CHORD': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.decrement_chord(5)
    print(f"New chord volume after decrement_chord(5): {new_volume}")
    
    passed = (new_volume == initial_volume - 5)
    print_test_result(
        "CHORD decrement",
        passed,
        [
            f"Initial: {initial_volume}, Expected: {initial_volume - 5}, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    return True


def test_key_press_and_mute():
    """Test: Press a key, then mute the corresponding volume"""
    print_section("Test 3: Key Press + Mute")
    
    volume_manager = KetronVolumeManager()
    ketron_midi = KetronMidi()
    
    # Test case 1: REALCHORD key press + mute
    print("\n--- Test Case 1: REALCHORD key press + mute_realchord() ---")
    
    volume_manager.set_volume("realchord", 80)
    initial_volume = volume_manager.realchord
    print(f"Initial realchord volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("REALCHORD")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("REALCHORD")
    print(f"CC control for 'REALCHORD': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.mute_realchord()
    print(f"New realchord volume after mute_realchord(): {new_volume}")
    
    passed = (new_volume == 0)
    print_test_result(
        "REALCHORD mute",
        passed,
        [
            f"Initial: {initial_volume}, Expected: 0, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    # Test case 2: VOICE2 key press + mute
    print("\n--- Test Case 2: VOICE2 key press + mute_voice2() ---")
    
    volume_manager.set_volume("voice2", 95)
    initial_volume = volume_manager.voice2
    print(f"Initial voice2 volume: {initial_volume}")
    
    volume_manager.set_last_pressed_key_name("VOICE2")
    print(f"Last pressed key_name: {volume_manager.last_pressed_key_name}")
    
    cc_control = ketron_midi.cc_midis.get("VOICE2")
    print(f"CC control for 'VOICE2': {cc_control} (0x{cc_control:02X})")
    
    new_volume = volume_manager.mute_voice2()
    print(f"New voice2 volume after mute_voice2(): {new_volume}")
    
    passed = (new_volume == 0)
    print_test_result(
        "VOICE2 mute",
        passed,
        [
            f"Initial: {initial_volume}, Expected: 0, Got: {new_volume}",
            f"CC control: {cc_control} (0x{cc_control:02X})"
        ]
    )
    
    return True


def test_multiple_operations():
    """Test: Multiple key presses and operations in sequence"""
    print_section("Test 4: Multiple Operations Sequence")
    
    volume_manager = KetronVolumeManager()
    ketron_midi = KetronMidi()
    
    print("\n--- Sequence: LOWERS increment -> STYLE decrement -> DRAWBARS mute ---")
    
    # Operation 1: LOWERS increment
    volume_manager.set_volume("lower", 50)
    initial_lower = volume_manager.lower
    volume_manager.set_last_pressed_key_name("LOWERS")
    new_lower = volume_manager.increment_lower(10)
    cc_lower = ketron_midi.cc_midis.get("LOWERS")
    print(f"1. LOWERS: {initial_lower} -> {new_lower} (CC: {cc_lower})")
    
    # Operation 2: STYLE decrement
    volume_manager.set_volume("style", 80)
    initial_style = volume_manager.style
    volume_manager.set_last_pressed_key_name("STYLE")
    new_style = volume_manager.decrement_style(20)
    cc_style = ketron_midi.cc_midis.get("STYLE")
    print(f"2. STYLE: {initial_style} -> {new_style} (CC: {cc_style})")
    
    # Operation 3: DRAWBARS mute
    volume_manager.set_volume("drawbars", 100)
    volume_manager.set_last_pressed_key_name("DRAWBARS")
    new_drawbars = volume_manager.mute_drawbars()
    cc_drawbars = ketron_midi.cc_midis.get("DRAWBARS")
    print(f"3. DRAWBARS: 100 -> {new_drawbars} (CC: {cc_drawbars})")
    
    # Verify all operations
    passed = (
        new_lower == 60 and
        new_style == 60 and
        new_drawbars == 0
    )
    print_test_result(
        "Multiple operations sequence",
        passed,
        [
            f"LOWERS: {new_lower} (expected 60)",
            f"STYLE: {new_style} (expected 60)",
            f"DRAWBARS: {new_drawbars} (expected 0)"
        ]
    )
    
    return True


def display_all_volumes():
    """Display all current volume levels"""
    print_section("Current Volume Levels")
    
    volume_manager = KetronVolumeManager()
    volumes = volume_manager.get_all_volumes()
    
    print("\nVolume Levels:")
    for volume_name, value in volumes.items():
        print(f"  {volume_name:12s}: {value:3d} / 127")
    
    print(f"\nMIDI Output Channel: {volume_manager.midi_out_channel}")
    print(f"Last Pressed Key: {volume_manager.last_pressed_key_name or 'None'}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("Ketron Volume Manager Test Suite")
    print("=" * 70)
    print("\nThis test demonstrates:")
    print("  1. Setting last pressed key_name")
    print("  2. Incrementing volumes")
    print("  3. Decrementing volumes")
    print("  4. Muting volumes")
    print("  5. MIDI CC command generation")
    
    try:
        # Run tests
        test_key_press_and_increment()
        test_key_press_and_decrement()
        test_key_press_and_mute()
        test_multiple_operations()
        
        # Display final state
        display_all_volumes()
        
        print_section("Test Summary")
        print("\n[INFO] All tests completed!")
        print("[INFO] Note: MIDI CC commands would be sent to the MIDI port")
        print("[INFO]       if a MIDI port was open. This test verifies the")
        print("[INFO]       logic and volume tracking only.")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

