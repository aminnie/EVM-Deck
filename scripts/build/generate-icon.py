#!/usr/bin/env python3
"""
Generate macOS application icon (.icns file) for DevDeck.

Creates an icon with "EVM" text in white on a ketron-blue background,
with rounded corners in macOS style.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Ketron blue color: RGB(0, 102, 204) = #0066CC
KETRON_BLUE = (0, 102, 204)
WHITE = (255, 255, 255)

# Icon sizes required for .icns format
ICON_SIZES = [
    (16, 16, "icon_16x16.png"),
    (32, 32, "icon_16x16@2x.png"),  # 2x variant
    (32, 32, "icon_32x32.png"),
    (64, 64, "icon_32x32@2x.png"),  # 2x variant
    (128, 128, "icon_128x128.png"),
    (256, 256, "icon_128x128@2x.png"),  # 2x variant
    (256, 256, "icon_256x256.png"),
    (512, 512, "icon_256x256@2x.png"),  # 2x variant
    (512, 512, "icon_512x512.png"),
    (1024, 1024, "icon_512x512@2x.png"),  # 2x variant
]


def get_font(size):
    """Get a font for the given size, trying system fonts first."""
    # Try common system fonts
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "arial.ttf",  # Windows
    ]
    
    # Try to load a system font
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # For .ttc files, we need to specify index
                if font_path.endswith('.ttc'):
                    return ImageFont.truetype(font_path, size, index=0)
                else:
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    
    # Fallback to default font
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        # Last resort: use default font
        return ImageFont.load_default()


def create_rounded_rectangle_mask(width, height, radius):
    """Create a mask for rounded rectangle (compatible with older PIL versions)."""
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw rounded rectangle using ellipses for corners
    # Draw main rectangle
    draw.rectangle([radius, 0, width - radius - 1, height - 1], fill=255)
    draw.rectangle([0, radius, width - 1, height - radius - 1], fill=255)
    
    # Draw corner circles
    draw.ellipse([0, 0, radius * 2, radius * 2], fill=255)  # Top-left
    draw.ellipse([width - radius * 2 - 1, 0, width - 1, radius * 2], fill=255)  # Top-right
    draw.ellipse([0, height - radius * 2 - 1, radius * 2, height - 1], fill=255)  # Bottom-left
    draw.ellipse([width - radius * 2 - 1, height - radius * 2 - 1, width - 1, height - 1], fill=255)  # Bottom-right
    
    return mask


def create_icon_image(width, height, text="EVM"):
    """Create a single icon image with rounded corners."""
    # Calculate corner radius (10% of size)
    corner_radius = int(min(width, height) * 0.1)
    
    # Create image with ketron-blue background
    img = Image.new('RGB', (width, height), KETRON_BLUE)
    
    # Create rounded rectangle mask
    mask = create_rounded_rectangle_mask(width, height, corner_radius)
    
    # Apply mask to create rounded corners
    output = Image.new('RGB', (width, height), KETRON_BLUE)
    output.paste(img, (0, 0), mask)
    draw = ImageDraw.Draw(output)
    
    # Calculate font size (approximately 60% of icon height)
    font_size = int(height * 0.6)
    font = get_font(font_size)
    
    # Get text bounding box to center it
    try:
        # Try new textbbox method (Pillow 8.0+)
        bbox = draw.textbbox((0, 0), text, font=font)
    except AttributeError:
        # Fallback for older Pillow versions
        bbox = draw.textsize(text, font=font)
        bbox = (0, 0, bbox[0], bbox[1])
    
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - bbox[1]  # Adjust for baseline
    
    # Draw text in white
    draw.text((x, y), text, fill=WHITE, font=font)
    
    return output


def generate_iconset(output_dir):
    """Generate all icon sizes in an .iconset directory."""
    iconset_dir = Path(output_dir) / "icon.iconset"
    
    # Remove existing iconset if it exists
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    
    iconset_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating icon images...")
    for width, height, filename in ICON_SIZES:
        print(f"  Creating {filename} ({width}x{height})...")
        img = create_icon_image(width, height)
        img.save(iconset_dir / filename, "PNG")
    
    print(f"Icon images generated in {iconset_dir}")
    return iconset_dir


def convert_to_icns(iconset_dir, output_file):
    """Convert .iconset directory to .icns file using iconutil."""
    output_path = Path(output_file)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing .icns file if it exists
    if output_path.exists():
        output_path.unlink()
    
    print(f"Converting .iconset to .icns...")
    
    # Use iconutil to convert iconset to icns
    try:
        result = subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully created {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting to .icns: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: iconutil command not found. This script must be run on macOS.", file=sys.stderr)
        return False


def main():
    """Main function to generate the icon."""
    # Get project root (assuming script is in scripts/build/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    assets_dir = project_root / "devdeck" / "assets"
    output_icns = assets_dir / "icon.icns"
    
    print("=== DevDeck Icon Generator ===")
    print(f"Project root: {project_root}")
    print(f"Output: {output_icns}")
    print()
    
    # Check if we're on macOS (iconutil is macOS-only)
    if sys.platform != 'darwin':
        print("Warning: This script is designed for macOS. iconutil may not be available.", file=sys.stderr)
        print("Continuing anyway...", file=sys.stderr)
    
    # Generate iconset
    iconset_dir = generate_iconset(assets_dir)
    
    # Convert to .icns
    if convert_to_icns(iconset_dir, output_icns):
        # Clean up iconset directory
        print(f"Cleaning up temporary .iconset directory...")
        shutil.rmtree(iconset_dir)
        print(f"\n✓ Icon generation complete: {output_icns}")
        return 0
    else:
        print(f"\n✗ Icon generation failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

