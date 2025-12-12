#!/bin/bash
# Build script for creating macOS .app bundle and .dmg installer
#
# This script:
# 1. Checks prerequisites (py2app, system libraries)
# 2. Builds the .app bundle using py2app
# 3. Bundles system libraries (libusb, hidapi)
# 4. Fixes library paths using install_name_tool
# 5. Creates a .dmg disk image

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Build configuration
APP_NAME="DevDeck"
DMG_NAME="${APP_NAME}"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
APP_BUNDLE="$DIST_DIR/${APP_NAME}.app"
FRAMEWORKS_DIR="$APP_BUNDLE/Contents/Frameworks"
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"

echo -e "${GREEN}=== DevDeck macOS Build Script ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Build directory: $BUILD_DIR"
echo "Dist directory: $DIST_DIR"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script must be run on macOS${NC}"
    exit 1
fi

# Check for Python 3.12+
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo -e "${RED}Error: Python 3.12+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}Python version OK: $PYTHON_VERSION${NC}"

# Check for py2app
echo -e "${YELLOW}Checking for py2app...${NC}"
if ! python3 -c "import py2app" 2>/dev/null; then
    echo -e "${YELLOW}py2app not found. Installing...${NC}"
    pip3 install py2app
fi
echo -e "${GREEN}py2app found${NC}"

# Detect architecture (Apple Silicon vs Intel)
ARCH=$(uname -m)
if [ "$ARCH" == "arm64" ]; then
    HOMEBREW_PREFIX="/opt/homebrew"
    echo -e "${GREEN}Detected Apple Silicon (ARM64)${NC}"
else
    HOMEBREW_PREFIX="/usr/local"
    echo -e "${GREEN}Detected Intel architecture${NC}"
fi

# Check for system libraries
echo -e "${YELLOW}Checking for system libraries...${NC}"
LIBUSB_PATH="$HOMEBREW_PREFIX/lib/libusb-1.0.dylib"
HIDAPI_PATH="$HOMEBREW_PREFIX/lib/libhidapi.dylib"

if [ ! -f "$LIBUSB_PATH" ]; then
    echo -e "${RED}Error: libusb not found at $LIBUSB_PATH${NC}"
    echo "Install with: brew install libusb"
    exit 1
fi

if [ ! -f "$HIDAPI_PATH" ]; then
    echo -e "${RED}Error: hidapi not found at $HIDAPI_PATH${NC}"
    echo "Install with: brew install hidapi"
    exit 1
fi
echo -e "${GREEN}System libraries found${NC}"

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf "$BUILD_DIR"
rm -rf "$DIST_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

# Build the .app bundle
echo -e "${YELLOW}Building .app bundle with py2app...${NC}"
cd "$PROJECT_ROOT"
python3 setup_macos.py py2app

if [ ! -d "$APP_BUNDLE" ]; then
    echo -e "${RED}Error: .app bundle not created${NC}"
    exit 1
fi
echo -e "${GREEN}.app bundle created successfully${NC}"

# Create Frameworks directory
mkdir -p "$FRAMEWORKS_DIR"

# Copy system libraries
echo -e "${YELLOW}Copying system libraries...${NC}"
cp "$LIBUSB_PATH" "$FRAMEWORKS_DIR/"
cp "$HIDAPI_PATH" "$FRAMEWORKS_DIR/"

# Get library IDs for reference
LIBUSB_ID="@executable_path/../Frameworks/libusb-1.0.dylib"
HIDAPI_ID="@executable_path/../Frameworks/libhidapi.dylib"

# Fix library paths in the copied libraries
echo -e "${YELLOW}Fixing library paths...${NC}"

# Fix libusb-1.0.dylib
install_name_tool -id "$LIBUSB_ID" "$FRAMEWORKS_DIR/libusb-1.0.dylib" 2>/dev/null || true

# Fix libhidapi.dylib
install_name_tool -id "$HIDAPI_ID" "$FRAMEWORKS_DIR/libhidapi.dylib" 2>/dev/null || true

# Update library references in Python extensions that might use these libraries
# Find all .so and .dylib files in the bundle and update their library paths
echo -e "${YELLOW}Updating library references in Python extensions...${NC}"
find "$APP_BUNDLE" -type f \( -name "*.so" -o -name "*.dylib" \) | while read lib; do
    # Update libusb references
    if otool -L "$lib" 2>/dev/null | grep -q "libusb-1.0"; then
        install_name_tool -change "$LIBUSB_PATH" "$LIBUSB_ID" "$lib" 2>/dev/null || true
    fi
    # Update hidapi references
    if otool -L "$lib" 2>/dev/null | grep -q "libhidapi"; then
        install_name_tool -change "$HIDAPI_PATH" "$HIDAPI_ID" "$lib" 2>/dev/null || true
    fi
done

# Update the main executable's library search path
EXECUTABLE="$APP_BUNDLE/Contents/MacOS/${APP_NAME}"
if [ -f "$EXECUTABLE" ]; then
    # Add Frameworks directory to library search path
    install_name_tool -add_rpath "@executable_path/../Frameworks" "$EXECUTABLE" 2>/dev/null || true
fi

echo -e "${GREEN}Library paths fixed${NC}"

# Remove quarantine attributes (allows unsigned apps to run)
echo -e "${YELLOW}Removing quarantine attributes...${NC}"
xattr -dr com.apple.quarantine "$APP_BUNDLE" 2>/dev/null || true
echo -e "${GREEN}Quarantine attributes removed${NC}"

# Verify executable exists and is valid
EXECUTABLE="$APP_BUNDLE/Contents/MacOS/${APP_NAME}"
if [ ! -f "$EXECUTABLE" ]; then
    echo -e "${RED}Error: Executable not found at $EXECUTABLE${NC}"
    echo -e "${RED}Build may have failed. Check py2app output above.${NC}"
    exit 1
fi

# Verify it's a valid file (not empty, has content)
if [ ! -s "$EXECUTABLE" ]; then
    echo -e "${RED}Error: Executable is empty or invalid${NC}"
    exit 1
fi

# Check file type
FILE_TYPE=$(file "$EXECUTABLE" 2>/dev/null || echo "unknown")
echo -e "${GREEN}Executable type: $FILE_TYPE${NC}"

# Make executable... executable (just in case)
chmod +x "$EXECUTABLE"

# Ad-hoc code sign the app (allows unsigned apps to run)
# This doesn't require a certificate, just makes macOS accept the binary
echo -e "${YELLOW}Ad-hoc code signing the application...${NC}"
codesign --force --deep --sign - "$APP_BUNDLE" 2>/dev/null || {
    echo -e "${YELLOW}Warning: Ad-hoc code signing failed, but continuing...${NC}"
    echo -e "${YELLOW}You may need to right-click and 'Open' the app the first time${NC}"
}

# Verify the signature (or lack thereof)
codesign --verify --verbose "$APP_BUNDLE" 2>/dev/null || echo -e "${YELLOW}App is not signed (expected for unsigned builds)${NC}"

echo -e "${GREEN}Code signing complete${NC}"

# Create .dmg
echo -e "${YELLOW}Creating .dmg disk image...${NC}"

# Create temporary directory for DMG contents
DMG_TEMP_DIR="$BUILD_DIR/dmg_temp"
rm -rf "$DMG_TEMP_DIR"
mkdir -p "$DMG_TEMP_DIR"

# Copy .app to temp directory
cp -R "$APP_BUNDLE" "$DMG_TEMP_DIR/"

# Create Applications symlink
ln -s /Applications "$DMG_TEMP_DIR/Applications"

# Calculate size needed for DMG (add 20% overhead)
APP_SIZE=$(du -sk "$APP_BUNDLE" | awk '{print $1}')
DMG_SIZE=$((APP_SIZE + 10000))  # Add 10MB overhead

# Create DMG
DMG_PATH="$DIST_DIR/${DMG_NAME}.dmg"
hdiutil create -srcfolder "$DMG_TEMP_DIR" \
    -volname "${APP_NAME}" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${DMG_SIZE}k \
    "$DMG_PATH.temp.dmg" > /dev/null

# Convert to read-only, compressed DMG
hdiutil convert "$DMG_PATH.temp.dmg" \
    -format UDZO \
    -o "$DMG_PATH" > /dev/null

# Clean up temp files
rm -f "$DMG_PATH.temp.dmg"
rm -rf "$DMG_TEMP_DIR"

echo -e "${GREEN}.dmg created successfully: $DMG_PATH${NC}"

# Summary
echo ""
echo -e "${GREEN}=== Build Complete ===${NC}"
echo "Application bundle: $APP_BUNDLE"
echo "Disk image: $DMG_PATH"
echo ""
echo "To test the application:"
echo "  open \"$APP_BUNDLE\""
echo ""
echo "If you get a security error, try:"
echo "  1. Right-click the app and select 'Open' (first time only)"
echo "  2. Or run: xattr -dr com.apple.quarantine \"$APP_BUNDLE\""
echo ""
echo "To distribute:"
echo "  Share the .dmg file: $DMG_PATH"
echo "  Users can drag ${APP_NAME}.app to their Applications folder"
echo "  Note: Users will need to right-click and 'Open' the first time"

