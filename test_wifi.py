"""
Test script for WiFi Manager functionality
Run this on the ESP32 to test the connection and AP mode
"""

from wifi_manager import WiFiManager
import time


def test_loading_spinner():
    """Test the LED loading spinner"""
    print("\n=== Testing Loading Spinner ===")
    manager = WiFiManager()

    print("Showing loading spinner for 5 seconds...")
    for i in range(50):  # 5 seconds at 0.1s per step
        manager.show_loading_spinner(i % manager.np.n)
        time.sleep(0.1)

    # Clear LEDs
    manager.np.fill((0, 0, 0))
    manager.np.write()
    print("Spinner test complete!")


def test_ap_mode():
    """Test Access Point mode"""
    print("\n=== Testing Access Point Mode ===")
    manager = WiFiManager()

    print("Starting AP mode...")
    manager.start_access_point()

    ap_ssid = manager.wlan_ap.config("essid")
    print(f"\nConnect to WiFi network: {ap_ssid}")
    print(f"Password: configure")
    print(f"Then visit: http://{manager.wlan_ap.ifconfig()[0]}")
    print("\nPress Ctrl+C to stop server")

    try:
        manager.serve_config_page()
    except KeyboardInterrupt:
        print("\nStopping AP mode...")
        manager.wlan_ap.active(False)


def test_full_connect():
    """Test full connection flow"""
    print("\n=== Testing Full Connection ===")
    manager = WiFiManager()

    result = manager.connect()

    if result:
        print("\n✓ Successfully connected to WiFi!")
        print(f"IP: {manager.wlan_sta.ifconfig()[0]}")
    else:
        print("\n✗ Connection failed, AP mode started")


# Uncomment the test you want to run:

# Test 1: Just the LED spinner
# test_loading_spinner()

# Test 2: AP mode and web server
# test_ap_mode()

# Test 3: Full connection flow (recommended)
test_full_connect()
