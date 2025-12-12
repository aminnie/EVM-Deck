# Next Steps & Future Work

This document tracks upcoming tasks and improvements for the DevDeck project, particularly around packaging and distribution.

## Immediate Next Steps

### macOS Build Testing
- [ ] **Test macOS build on Mac Mini**
  - Checkout `build/macos-packaging` branch
  - Run `./scripts/build/build-macos.sh`
  - Verify `.app` bundle runs correctly
  - Test USB device detection (Stream Deck, MIDI)
  - Verify GUI functionality
  - Test `.dmg` installation process

- [ ] **Test on clean macOS system**
  - Test bundle on system without Python/Homebrew installed
  - Verify all dependencies are bundled correctly
  - Check library loading (libusb, hidapi)

- [ ] **Document any build issues**
  - Update `docs/MACOS_PACKAGING.md` with solutions
  - Add troubleshooting steps as needed

## Future Build Targets

### Raspberry Pi Packaging
- [ ] **Create Raspberry Pi build branch**
  - Branch: `build/raspberry-pi`
  - Base from `main` branch

- [ ] **Research packaging options**
  - Consider: `.deb` package, systemd service, or custom installer
  - Review existing `docs/RASPBERRY_PI_DEPLOYMENT.md` for requirements
  - Determine if we need: `setup.py`, `setup_raspberry_pi.py`, or other

- [ ] **Create Raspberry Pi build script**
  - `scripts/build/build-raspberry-pi.sh`
  - Package Python dependencies
  - Include systemd service files
  - Create installable package

- [ ] **Documentation**
  - Create `docs/RASPBERRY_PI_PACKAGING.md`
  - Update `scripts/build/README.md`

### Windows Packaging (Optional)
- [ ] **Research Windows packaging options**
  - Consider: PyInstaller, cx_Freeze, or NSIS installer
  - Evaluate requirements for Windows build

- [ ] **Create Windows build branch** (if needed)
  - Branch: `build/windows-packaging`
  - Create build scripts and documentation

## Code Improvements

### Path Utilities
- [ ] **Test path_utils in both modes**
  - Verify development mode paths work correctly
  - Verify bundle mode paths work correctly
  - Test edge cases (missing directories, permissions)

### Build Scripts
- [ ] **Add error handling improvements**
  - Better error messages in build script
  - Validation of build output
  - Automated testing of built bundles

- [ ] **Add build versioning**
  - Automatically extract version from git tags
  - Include version in `.app` bundle and `.dmg`
  - Update `setup_macos.py` to use dynamic versioning

## Distribution

### Code Signing (Optional - for public distribution)
- [ ] **Research code signing requirements**
  - Apple Developer account setup
  - Code signing process
  - Notarization requirements

- [ ] **Implement code signing** (if distributing publicly)
  - Update build script to sign bundle
  - Add notarization step
  - Document signing process

### Release Process
- [ ] **Create release workflow**
  - Tagged releases with builds
  - Automated build on release tags
  - Distribution of `.dmg` files

## Documentation Updates

- [ ] **Update main README.md**
  - Add section on building/packaging
  - Link to build documentation
  - Add download/installation instructions

- [ ] **Create user installation guide**
  - Step-by-step for end users
  - Screenshots of installation process
  - Troubleshooting common issues

## Testing & Quality

- [ ] **Create build validation tests**
  - Automated checks for bundle structure
  - Verify all dependencies included
  - Test on multiple macOS versions

- [ ] **User acceptance testing**
  - Test with actual users
  - Gather feedback on installation process
  - Document common issues

## Notes

### Current Status
- ✅ macOS build infrastructure complete
- ✅ Branch structure established
- ✅ Documentation created
- ⏳ Awaiting first build test on macOS

### Known Considerations
- Code signing not implemented (for personal/internal use only)
- Build tested on Windows development environment only
- Raspberry Pi build structure not yet defined

### Resources
- macOS Build: `docs/MACOS_PACKAGING.md`
- Build Workflow: `docs/BUILD_WORKFLOW.md`
- Build Scripts: `scripts/build/README.md`
- Raspberry Pi Deployment: `docs/RASPBERRY_PI_DEPLOYMENT.md` (existing)

---

**Last Updated**: [Date will be updated as work progresses]

**Branch**: `build/macos-packaging`

