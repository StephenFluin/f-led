"""
Boot script for ESP32 Sports LED Display
Handles WiFi connection with Access Point fallback
"""

from wifi_manager import connect_wifi

# Connect to WiFi (or start AP mode if connection fails)
print("=" * 50)
print("ESP32 Sports LED Display - Booting")
print("=" * 50)

connect_wifi()

print("=" * 50)
print("Boot complete!")
print("=" * 50)
