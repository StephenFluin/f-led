"""
WiFi Manager with Access Point fallback and configuration web server
"""

import network
import socket
import time
import machine
import neopixel
import ubinascii
from config import get_wifi_credentials, update_wifi_credentials
from template_loader import load_template, render_template, serve_html
from utils import url_decode_params
import constants


def get_ap_ssid():
    """Generate unique AP SSID using MAC address"""
    mac = ubinascii.hexlify(network.WLAN().config("mac")).decode()
    # Use last 4 characters of MAC as unique code
    code = mac[-4:].upper()
    return f"{constants.AP_SSID_PREFIX}-{code}"


class WiFiManager:
    def __init__(self):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.np = neopixel.NeoPixel(machine.Pin(constants.DATA_PIN), constants.NUM_LEDS)
        self.connected = False

    def show_loading_spinner(self, position):
        """Show blue loading spinner at 5% brightness"""
        self.np.fill((0, 0, 0))
        # Show current LED in blue
        if position < constants.NUM_LEDS:
            self.np[position] = (0, 0, constants.LOADING_BRIGHTNESS_VALUE)
        self.np.write()

    def try_connect_sta(self, ssid, password, hostname, timeout=None):
        """Try to connect to WiFi in station mode with loading spinner"""
        if timeout is None:
            timeout = constants.WIFI_CONNECT_TIMEOUT_SEC

        if not ssid:
            print("No SSID configured")
            return False

        self.wlan_sta.active(True)

        # Set hostname
        try:
            self.wlan_sta.config(dhcp_hostname=hostname)
        except Exception as e:
            print(f"Warning: Could not set hostname: {e}")

        if self.wlan_sta.isconnected():
            print("Already connected to WiFi")
            self.connected = True
            return True

        print(f"Connecting to {ssid} as '{hostname}'...")
        self.wlan_sta.connect(ssid, password)

        # Wait for connection with loading spinner
        max_wait = timeout * 10  # Check every 0.1 seconds
        led_position = 0

        while max_wait > 0:
            if self.wlan_sta.isconnected():
                # Clear LEDs after successful connection
                self.np.fill((0, 0, 0))
                self.np.write()
                print("Wi-Fi Connected!")
                print(f"IP Address: {self.wlan_sta.ifconfig()[0]}")
                print(f"Hostname: {hostname}")
                self.connected = True
                return True

            # Update loading spinner
            self.show_loading_spinner(led_position)
            led_position = (led_position + 1) % constants.NUM_LEDS

            max_wait -= 1
            time.sleep(constants.WIFI_CHECK_INTERVAL_SEC)

        print("Failed to connect to WiFi")
        self.wlan_sta.active(False)
        return False

    def start_access_point(self):
        """Start access point mode for configuration"""
        ap_ssid = get_ap_ssid()
        print(f"Starting Access Point: {ap_ssid}")
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=ap_ssid, password=constants.AP_PASSWORD)

        # Wait for AP to be active
        while not self.wlan_ap.active():
            time.sleep(0.1)

        print(f"AP Started: {ap_ssid}")
        print(f"AP Password: {constants.AP_PASSWORD}")
        print(f"AP IP: {self.wlan_ap.ifconfig()[0]}")
        return True

    def serve_config_page(self):
        """Serve configuration web page"""
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)

        print("Configuration server running on port 80")
        print(f"Visit: http://{self.wlan_ap.ifconfig()[0]}")

        while True:
            try:
                cl, addr = s.accept()
                print(f"Client connected from {addr}")
                request = cl.recv(1024).decode("utf-8")

                # Parse request
                if "GET / " in request or "GET /config" in request:
                    response = self.get_config_html()
                elif "POST /save" in request:
                    response = self.handle_config_save(request)
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

                cl.send(response.encode("utf-8"))
                cl.close()

            except OSError as e:
                print(f"Server error: {e}")
                cl.close()

    def get_config_html(self):
        """Generate configuration HTML page"""
        ssid, password, hostname = get_wifi_credentials()
        ap_ssid = get_ap_ssid()
        device_code = ap_ssid.split("-")[1]

        template = load_template("wifi_config.html")
        html_content = render_template(
            template,
            DEVICE_CODE=device_code,
            SSID=ssid,
            PASSWORD=password,
            HOSTNAME=hostname,
        )

        return serve_html(html_content)

    def handle_config_save(self, request):
        """Handle configuration save from POST request"""
        try:
            # Extract form data from POST request
            body = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
            params = url_decode_params(body)

            ssid = params.get("ssid", "")
            password = params.get("password", "")
            hostname = params.get("hostname", "wildsensor")

            if ssid and password:
                update_wifi_credentials(ssid, password, hostname)

                template = load_template("wifi_saved.html")
                response = serve_html(template)

                # Schedule restart after sending response
                # Give time for the response to be sent
                time.sleep(3)
                machine.reset()

                return response
            else:
                return "HTTP/1.1 400 Bad Request\r\n\r\nInvalid parameters"

        except Exception as e:
            print(f"Error saving config: {e}")
            return f"HTTP/1.1 500 Internal Server Error\r\n\r\nError: {e}"

    def connect(self):
        """Main connection logic with fallback to AP mode"""
        ssid, password, hostname = get_wifi_credentials()

        # Try to connect to configured WiFi
        if self.try_connect_sta(ssid, password, hostname):
            return True

        # If connection failed, start AP mode
        print("Could not connect to WiFi. Starting configuration mode...")
        self.start_access_point()

        # Show solid blue at 5% brightness to indicate AP mode
        self.np.fill(constants.COLOR_BLUE_AP_MODE)
        self.np.write()

        # Serve configuration page
        self.serve_config_page()

        return False


def connect_wifi():
    """Helper function for backward compatibility"""
    manager = WiFiManager()
    return manager.connect()
