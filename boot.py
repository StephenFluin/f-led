"""
Boot script for ESP32 Sports LED Display
Handles WiFi connection with Access Point fallback
"""

from wifi_manager import connect_wifi
import constants
import network

# Connect to WiFi (or start AP mode if connection fails)
print("=" * 50)
print("ESP32 Sports LED Display - Booting")
print("=" * 50)

wifi_connected = connect_wifi()

# Start configuration server if WiFi connected successfully
if wifi_connected:
    try:
        from config_server import start_config_server

        # Get IP address
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print("\n" + "=" * 50)
            print("Configuration Server Starting...")
            print(f"Access at: http://{ip}")
            print("=" * 50 + "\n")

            # Start config server in background
            start_config_server(port=constants.DEFAULT_HTTP_PORT, background=True)
    except Exception as e:
        print(f"Note: Config server not started: {e}")
        print("Device will continue normal operation.")

print("=" * 50)
print("Boot complete!")
print("=" * 50)
