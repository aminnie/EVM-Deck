#!/usr/bin/env python3
"""
Generate a random JSON structure containing key mappings for all 30 keys (0-29)
from pedal_midis, tab_midis, or cc_midis lists.
"""

import json
import random
import sys
import os

# Add devdeck directory to path to import ketron
# Get the project root (parent of scripts directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from devdeck.ketron import KetronMidi

def generate_random_mappings():
    """Generate random mappings for all 30 keys"""
    # Create a minimal KetronMidi instance without calling _build_cache
    ketron = KetronMidi.__new__(KetronMidi)
    ketron.pedal_midis = ketron._init_pedal_midis()
    ketron.tab_midis = ketron._init_tab_midis()
    ketron.cc_midis = ketron._init_cc_midis()
    
    # Get all available keys from each list
    pedal_keys = list(ketron.pedal_midis.keys())
    tab_keys = list(ketron.tab_midis.keys())
    cc_keys = list(ketron.cc_midis.keys())
    
    # Create list of (list_name, keys) tuples
    all_lists = [
        ("pedal_midis", pedal_keys),
        ("tab_midis", tab_keys),
        ("cc_midis", cc_keys)
    ]
    
    mappings = []
    for key_no in range(30):
        # Randomly select a source list
        source_list_name, keys = random.choice(all_lists)
        # Randomly select a key from that list
        key_name = random.choice(keys)
        
        mappings.append({
            "key_no": key_no,
            "key_name": key_name,
            "source_list_name": source_list_name,
            "text_color": "white",
            "background_color": "black"
        })
    
    return mappings

if __name__ == "__main__":
    mappings = generate_random_mappings()
    # Structure with a named key for better organization
    output = {
        "key_mappings": mappings
    }
    
    # Write to config directory
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    os.makedirs(config_dir, exist_ok=True)
    output_file = os.path.join(config_dir, 'key_mappings.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {len(mappings)} key mappings and saved to {output_file}")

