# Quick Setup Guide

## What's New?

Your ESP32 sports display now has:

1. **Web-based WiFi configuration** - No more hardcoded credentials!
2. **Access Point fallback** - Automatic setup mode when WiFi fails
3. **Blue loading spinner** - Visual feedback at 5% brightness during connection
4. **Persistent storage** - Configuration saved to `config.json`

## Setup Flow

### Option 1: First Time Setup (No WiFi Configured)

1. **Power on ESP32**

   - LEDs show blue loading spinner for 15 seconds
   - Device enters Access Point mode (solid blue at 5%)

2. **Connect to WiFi**

   - Network: `scorebox-XXXX` (XXXX is a unique code from your device)
   - Password: `configure`

3. **Configure Device**

   - Open browser: `http://192.168.4.1`
   - Enter your WiFi credentials
   - Click "Save & Restart"

4. **Done!**
   - Device connects to your WiFi
   - Normal operation begins

### Option 2: Upload Config File

If you prefer to skip the web interface:

1. **Create config.json**

   ```python
   # Run on ESP32 or create file locally
   from config_helper import create_config_file
   create_config_file(
       ssid="YourWiFiNetwork",
       password="YourPassword",
       hostname="wildsensor",
       team_abbrev="MIN",
       poll_interval=10,
       num_leds=48
   )
   ```

2. **Upload to ESP32**

   - Use Thonny or your preferred tool
   - Upload the generated `config.json`

3. **Restart ESP32**
   - Device will use the new configuration

## Files to Upload to ESP32

**Required files:**

- `boot.py` - Handles WiFi on startup
- `main.py` - Main application (your existing code, updated)
- `wifi_manager.py` - WiFi management with AP mode
- `config.py` - Configuration file handling

**Optional files:**

- `config_helper.py` - Helper functions for config management
- `config_server.py` - Run config web server even when WiFi connected
- `test_wifi.py` - Test WiFi functionality

## Testing

### Test WiFi Manager

```python
# On ESP32, run:
import test_wifi
# Uncomment the test you want in test_wifi.py
```

### Test Loading Spinner

The spinner will show automatically when:

- Device boots and tries to connect
- WiFi credentials are wrong or network unavailable

### Test AP Mode

Delete or rename `config.json`, then restart the device.

## Advanced: Run Config Server While Connected

If you want to access configuration web interface even when device is connected to WiFi:

```python
# Add to main.py after WiFi connects:
from config_server import start_config_server

# Start server on port 8080 (doesn't interfere with main app)
config_server = start_config_server(port=8080, background=True)

# Access at: http://[device-ip]:8080
```

## LED Indicators Reference

| Pattern                      | Meaning                          |
| ---------------------------- | -------------------------------- |
| Blue spinner (5% brightness) | Connecting to WiFi               |
| Solid blue (5% brightness)   | AP mode - ready for config       |
| Off                          | WiFi connected, waiting for data |
| Green points                 | Your team's score                |
| Red points                   | Opponent's score                 |
| Pulsing green/red            | Goal celebration!                |

## Troubleshooting

**Q: LEDs stay blue forever**

- WiFi credentials might be wrong
- Wait 15 seconds for AP mode to activate
- Connect to `scorebox-XXXX` and reconfigure

**Q: Can't see scorebox-XXXX network**

- Wait 30 seconds after boot
- Make sure you're looking for 2.4GHz networks (ESP32 doesn't support 5GHz)
- Try restarting the device

**Q: Configuration page won't load**

- Make sure you're connected to `scorebox-XXXX` network
- Try `http://192.168.4.1` exactly
- Some phones need "Stay connected" when it says "No Internet"

**Q: Want to change team or settings**

- Connect to device's WiFi network
- Use web interface at `http://192.168.4.1` (AP mode)
- Or use `config_helper.py` functions

## Configuration Parameters

### WiFi Settings

- **ssid**: Your WiFi network name
- **password**: Your WiFi password
- **hostname**: Device name on network (default: "wildsensor")

### Device Settings

- **team_abbrev**: 3-letter team code (e.g., "MIN", "CHI", "BOS")
- **poll_interval**: Seconds between API checks (default: 10)
- **num_leds**: Total LEDs in your strip (default: 48)

## Example Workflows

### Change Team

```python
from config_helper import update_team
update_team("CHI")  # Change to Chicago Blackhawks
```

### Change WiFi

```python
from config_helper import update_wifi
update_wifi("NewNetwork", "NewPassword")
```

### View Current Config

```python
from config_helper import show_config
show_config()
```

## Next Steps

1. Upload all files to your ESP32
2. Restart the device
3. Configure via web interface
4. Watch your team's games! 🏒

Enjoy your upgraded device! 🎉
