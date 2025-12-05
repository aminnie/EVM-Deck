"""
Boot Logo Updater for Stream Deck Module 15/32 using HID API.

This module implements the boot logo update functionality using the direct HID protocol
as specified in the Elgato Stream Deck HID API documentation.
"""

import io
import logging
import struct
from pathlib import Path
from typing import Optional

try:
    import hid
except ImportError:
    hid = None

from PIL import Image


# Stream Deck Module device IDs
STREAM_DECK_MODULE_15_VID = 0x0FD9
STREAM_DECK_MODULE_15_PID = 0x00B9
STREAM_DECK_MODULE_32_VID = 0x0FD9
STREAM_DECK_MODULE_32_PID = 0x00BA

# HID Protocol constants
OUTPUT_REPORT_ID = 0x02
BOOT_LOGO_COMMAND = 0x09
MAX_OUTPUT_REPORT_SIZE = 1024
HEADER_SIZE = 8  # Report ID (1) + Command (1) + Reserved (1) + Transfer Done (1) + Chunk Index (2) + Chunk Size (2)


class BootLogoUpdater:
    """Updates the boot logo on Stream Deck Module 15/32 devices using HID API."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the boot logo updater.
        
        Args:
            logger: Optional logger instance. If None, creates a new logger.
        """
        self.logger = logger or logging.getLogger('devdeck.boot_logo')
        
        if hid is None:
            self.logger.warning("hid library not available. Boot logo update will be disabled.")
            self._hid_available = False
        else:
            self._hid_available = True
    
    def find_device(self) -> Optional[hid.device]:
        """
        Find and open a Stream Deck Module device.
        
        Returns:
            Open HID device handle, or None if not found or unavailable.
        """
        if not self._hid_available:
            return None
        
        try:
            # Try Module 15 first
            device = hid.device()
            device.open(STREAM_DECK_MODULE_15_VID, STREAM_DECK_MODULE_15_PID)
            self.logger.info("Found Stream Deck Module 15")
            return device
        except (OSError, IOError):
            pass
        
        try:
            # Try Module 32
            device = hid.device()
            device.open(STREAM_DECK_MODULE_32_VID, STREAM_DECK_MODULE_32_PID)
            self.logger.info("Found Stream Deck Module 32")
            return device
        except (OSError, IOError):
            pass
        
        self.logger.warning("Stream Deck Module device not found")
        return None
    
    def prepare_image(self, image_path: Path) -> bytes:
        """
        Prepare the boot logo image according to specifications.
        
        Requirements:
        - Must be rotated 180° for all unit models
        - Must be in JPEG format
        - Size: 480×272 for Module 15, 1024×600 for Module 32
        
        Args:
            image_path: Path to the image file
            
        Returns:
            JPEG image data as bytes
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Boot logo image not found: {image_path}")
        
        # Load and process image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Rotate 180° as required by the API
        img = img.rotate(180, expand=False)
        
        # Save to JPEG in memory
        jpeg_buffer = io.BytesIO()
        # Use quality 85 as a balance between size and quality
        # May need to reduce if image is too large
        img.save(jpeg_buffer, format='JPEG', quality=85, optimize=True)
        
        jpeg_data = jpeg_buffer.getvalue()
        self.logger.info(f"Prepared boot logo image: {len(jpeg_data)} bytes")
        
        return jpeg_data
    
    def update_boot_logo(self, image_path: Path) -> bool:
        """
        Update the boot logo on the Stream Deck Module.
        
        Args:
            image_path: Path to the boot logo image file
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hid_available:
            self.logger.error("HID library not available. Cannot update boot logo.")
            return False
        
        device = None
        try:
            # Find and open device
            device = self.find_device()
            if device is None:
                self.logger.warning("Stream Deck Module not found. Skipping boot logo update.")
                return False
            
            # Prepare image
            image_data = self.prepare_image(image_path)
            
            # Calculate chunk size (max report size minus header)
            chunk_size = MAX_OUTPUT_REPORT_SIZE - HEADER_SIZE
            total_chunks = (len(image_data) + chunk_size - 1) // chunk_size
            
            self.logger.info(f"Uploading boot logo: {len(image_data)} bytes in {total_chunks} chunks")
            
            # Send image in chunks
            for chunk_index in range(total_chunks):
                is_last_chunk = (chunk_index == total_chunks - 1)
                start_offset = chunk_index * chunk_size
                end_offset = min(start_offset + chunk_size, len(image_data))
                chunk_data = image_data[start_offset:end_offset]
                
                # Build output report
                report = bytearray(MAX_OUTPUT_REPORT_SIZE)
                report[0] = OUTPUT_REPORT_ID
                report[1] = BOOT_LOGO_COMMAND
                report[2] = 0x00  # Reserved
                report[3] = 0x01 if is_last_chunk else 0x00  # Transfer is Done flag
                struct.pack_into('<H', report, 4, chunk_index)  # Chunk Index (little-endian)
                struct.pack_into('<H', report, 6, len(chunk_data))  # Chunk Contents Size
                
                # Copy chunk data
                report[HEADER_SIZE:HEADER_SIZE + len(chunk_data)] = chunk_data
                
                # Send report
                device.write(report)
                
                if (chunk_index + 1) % 10 == 0 or is_last_chunk:
                    self.logger.debug(f"Sent chunk {chunk_index + 1}/{total_chunks}")
            
            self.logger.info("Boot logo updated successfully")
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"Boot logo image not found: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update boot logo: {e}", exc_info=True)
            return False
        finally:
            if device is not None:
                try:
                    device.close()
                except Exception:
                    pass
    
    def update_boot_logo_if_exists(self, image_path: Optional[Path] = None) -> bool:
        """
        Update boot logo if image file exists, otherwise skip silently.
        
        Args:
            image_path: Optional path to boot logo image. If None, uses default path.
            
        Returns:
            True if update was attempted and successful, False otherwise
        """
        if image_path is None:
            # Default to Ketron480-272.jpg in assets directory
            project_root = Path(__file__).parent.parent
            image_path = project_root / 'devdeck' / 'assets' / 'Ketron480-272.jpg'
        
        if not image_path.exists():
            self.logger.debug(f"Boot logo image not found at {image_path}, skipping update")
            return False
        
        return self.update_boot_logo(image_path)

