# ESP32 Sports LED Display

A network-connected ESP32 device that monitors sports API endpoints and displays live scores with LED feedback and goal celebrations.

## Features

- **WiFi Configuration**: Web-based setup interface
- **Access Point Fallback**: Automatically creates a WiFi hotspot when unable to connect
- **Loading Indicator**: Blue LED spinner at 5% brightness during WiFi connection
- **Persistent Configuration**: Saves WiFi credentials and settings to device storage
- **Live Score Display**: Shows current game score on LED matrix
- **Goal Celebrations**: Visual and audio effects when goals are scored

## Initial Setup

### First Time Configuration

1. **Power on the device**

   - The device will attempt to connect to a saved WiFi network
   - If no configuration exists or connection fails, it will enter AP mode

2. **Connect to Configuration Portal**

   - Look for WiFi network: `scorebox-XXXX` (where XXXX is a unique code)
   - Password: `configure`
   - Connect to this network with your phone or computer

3. **Configure WiFi**

   - Open browser and navigate to: `http://192.168.4.1`
   - Enter your WiFi network credentials:
     - SSID (network name)
     - Password
     - Device hostname (default: wildsensor)
   - Click "Save & Restart"

4. **Device Restart**
   - The device will restart and connect to your WiFi network
   - Blue LEDs will show a loading spinner during connection
   - Once connected, LEDs will turn off and normal operation begins

### Reconfiguration

If you need to change WiFi settings:

1. Delete the `config.json` file from the device, or
2. Set WiFi credentials that won't connect to trigger AP mode
3. Follow the initial setup steps above

## LED Indicators

- **Blue Spinner (5% brightness)**: WiFi connection in progress
- **Solid Blue (5% brightness)**: Access Point mode active (ready for configuration)
- **Green**: Your team's score points
- **Red**: Opponent's score points
- **Pulsing Green/Red**: Goal celebration

## Configuration Files

### config.json

Stores device configuration including:

```json
{
  "wifi": {
    "ssid": "YourNetwork",
    "password": "YourPassword",
    "hostname": "wildsensor"
  },
  "device": {
    "team_abbrev": "MIN",
    "poll_interval": 10,
    "num_leds": 48
  }
}
```

### score.txt

Caches the last known score to maintain state across reboots.

## Hardware

- ESP32 Development Board
- WS2812B LED Strip (48 LEDs default)
- Optional: Buzzer for goal celebrations
- Optional: Relay module

### Pin Configuration

- **DATA_PIN**: 16 (LED data)
- **RELAY_PIN**: 12 (Relay control)
- **BUZZER_PIN**: 25 (Buzzer PWM)

## Files

- `boot.py`: Handles WiFi connection on startup
- `main.py`: Main application logic for score monitoring and LED control
- `wifi_manager.py`: WiFi management with AP fallback and web server
- `config.py`: Configuration file management
- `config.json`: Device configuration (created on first setup)

## API

The device polls the NHL API:

```
https://api-web.nhle.com/v1/score/now
```

## Development

To modify the code:

1. Connect to the ESP32 via USB
2. Use Thonny IDE or similar MicroPython tool
3. Edit files and upload to the device
4. Reset the device to apply changes

## Troubleshooting

**LEDs show blue spinner indefinitely**

- WiFi credentials may be incorrect
- Wait for timeout (15 seconds), device will enter AP mode
- Reconfigure via the web interface

**Can't connect to scorebox-XXXX network**

- Make sure device has fully booted (wait 30 seconds)
- Check that your device supports 2.4GHz WiFi
- Try resetting the ESP32
- The XXXX code is unique to your device based on its MAC address

**No LED activity**

- Check LED strip connections
- Verify DATA_PIN (16) is correct for your hardware
- Check power supply to LED strip

## License

MIT License - Feel free to modify and use for your own projects!
