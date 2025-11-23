# PowerShell script to check MIDI device information in Windows

Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host "Windows MIDI Device Information"
Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host ""

# Check Windows Registry for MIDI devices
Write-Host "Checking Windows Registry for MIDI devices..."
Write-Host "-" -NoNewline
Write-Host ("-" * 69)

try {
    $midiPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Multimedia\Sound Mapper"
    if (Test-Path $midiPath) {
        $midiDevices = Get-ItemProperty $midiPath -ErrorAction SilentlyContinue
        if ($midiDevices) {
            Write-Host "MIDI devices found in registry:"
            $midiDevices.PSObject.Properties | Where-Object { 
                $_.Name -notlike "PS*" -and $_.Name -ne "Path" 
            } | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value)"
            }
        } else {
            Write-Host "No MIDI device properties found in registry"
        }
    } else {
        Write-Host "MIDI registry path not found: $midiPath"
    }
} catch {
    Write-Host "Error accessing registry: $_"
}

Write-Host ""
Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host "Active MIDI Ports (via WMI)"
Write-Host "-" -NoNewline
Write-Host ("-" * 69)

# Check for MIDI devices via WMI (if available)
try {
    $soundDevices = Get-WmiObject Win32_SoundDevice -ErrorAction SilentlyContinue
    if ($soundDevices) {
        Write-Host "Sound devices found:"
        $soundDevices | ForEach-Object {
            Write-Host "  $($_.Name)"
        }
    } else {
        Write-Host "No sound devices found via WMI"
    }
} catch {
    Write-Host "WMI query not available or failed"
}

Write-Host ""
Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host "How to Check Application MIDI Identity"
Write-Host "-" -NoNewline
Write-Host ("-" * 69)
Write-Host ""
Write-Host "1. Run your application (devdeck)"
Write-Host "2. Open MidiView or another MIDI monitoring tool"
Write-Host "3. Look for active MIDI connections"
Write-Host "4. The application will appear with the port name it opens"
Write-Host ""
Write-Host "On Windows:"
Write-Host "  - Hardware MIDI ports show their driver/device name"
Write-Host "  - Example: 'MidiView 1' appears as the MidiView driver name"
Write-Host "  - Virtual ports (if supported) would show the custom name"
Write-Host ""
Write-Host "To see what port your application opened:"
Write-Host "  - Check the application logs for 'Opened MIDI output port: ...'"
Write-Host "  - That port name is what appears in MIDI monitoring software"
Write-Host ""


