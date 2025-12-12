#!/bin/bash
# Diagnostic script to check .app bundle structure and executable

set -e

APP_BUNDLE="${1:-dist/DevDeck.app}"

if [ ! -d "$APP_BUNDLE" ]; then
    echo "Error: App bundle not found at $APP_BUNDLE"
    exit 1
fi

EXECUTABLE="$APP_BUNDLE/Contents/MacOS/DevDeck"

echo "=== DevDeck App Bundle Diagnostics ==="
echo ""

echo "1. Checking bundle structure..."
ls -la "$APP_BUNDLE/Contents/"
echo ""

echo "2. Checking MacOS directory..."
ls -la "$APP_BUNDLE/Contents/MacOS/"
echo ""

echo "3. Checking executable..."
if [ -f "$EXECUTABLE" ]; then
    echo "  Executable exists: YES"
    echo "  Size: $(ls -lh "$EXECUTABLE" | awk '{print $5}')"
    echo "  Permissions: $(ls -l "$EXECUTABLE" | awk '{print $1}')"
    echo ""
    echo "  File type:"
    file "$EXECUTABLE"
    echo ""
    echo "  First 20 lines:"
    head -20 "$EXECUTABLE"
    echo ""
    echo "  Code signature:"
    codesign -dv "$EXECUTABLE" 2>&1 || echo "  Not signed or invalid"
    echo ""
else
    echo "  Executable exists: NO"
    echo "  ERROR: Executable not found!"
fi

echo "4. Checking Resources directory..."
if [ -d "$APP_BUNDLE/Contents/Resources" ]; then
    echo "  Resources directory exists: YES"
    echo "  Contents:"
    ls -la "$APP_BUNDLE/Contents/Resources" | head -20
    echo ""
    
    # Check for Python
    if [ -f "$APP_BUNDLE/Contents/Resources/lib" ] || [ -d "$APP_BUNDLE/Contents/Resources/lib" ]; then
        echo "  Python lib found: YES"
    else
        echo "  Python lib found: NO"
    fi
else
    echo "  Resources directory exists: NO"
fi

echo "5. Checking Info.plist..."
if [ -f "$APP_BUNDLE/Contents/Info.plist" ]; then
    echo "  Info.plist exists: YES"
    echo "  Contents:"
    cat "$APP_BUNDLE/Contents/Info.plist"
else
    echo "  Info.plist exists: NO"
fi

echo ""
echo "6. Attempting to run executable directly..."
if [ -f "$EXECUTABLE" ]; then
    echo "  Running: $EXECUTABLE"
    "$EXECUTABLE" 2>&1 | head -50 || echo "  Failed to run"
else
    echo "  Cannot run - executable not found"
fi

