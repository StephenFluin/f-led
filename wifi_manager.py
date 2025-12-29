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

# AP Mode defaults
AP_PASSWORD = "configure"


def get_ap_ssid():
    """Generate unique AP SSID using MAC address"""
    mac = ubinascii.hexlify(network.WLAN().config("mac")).decode()
    # Use last 4 characters of MAC as unique code
    code = mac[-4:].upper()
    return f"scorebox-{code}"


# LED setup for loading spinner
DATA_PIN = 16
NUM_LEDS = 48


class WiFiManager:
    def __init__(self):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.np = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)
        self.connected = False

    def show_loading_spinner(self, position):
        """Show blue loading spinner at 5% brightness"""
        self.np.fill((0, 0, 0))
        # 5% of 255 = 12.75, round to 13
        brightness = 13
        # Show current LED in blue
        if position < NUM_LEDS:
            self.np[position] = (0, 0, brightness)
        self.np.write()

    def try_connect_sta(self, ssid, password, hostname, timeout=15):
        """Try to connect to WiFi in station mode with loading spinner"""
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
            led_position = (led_position + 1) % NUM_LEDS

            max_wait -= 1
            time.sleep(0.1)

        print("Failed to connect to WiFi")
        self.wlan_sta.active(False)
        return False

    def start_access_point(self):
        """Start access point mode for configuration"""
        ap_ssid = get_ap_ssid()
        print(f"Starting Access Point: {ap_ssid}")
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=ap_ssid, password=AP_PASSWORD)

        # Wait for AP to be active
        while not self.wlan_ap.active():
            time.sleep(0.1)

        print(f"AP Started: {ap_ssid}")
        print(f"AP Password: {AP_PASSWORD}")
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

        html = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ScoreBox WiFi Configuration</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        label {{
            display: block;
            margin: 15px 0 5px 0;
            color: #555;
            font-weight: bold;
        }}
        input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 16px;
        }}
        button {{
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            margin-top: 20px;
        }}
        button:hover {{
            background: #0056b3;
        }}
        .info {{
            background: #e7f3ff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ScoreBox {ap_ssid.split('-')[1]}</h1>
        <div class="info">
            Configure your WiFi credentials. The device will restart and connect to your network.
        </div>
        <form action="/save" method="POST">
            <label for="ssid">WiFi Network (SSID):</label>
            <input type="text" id="ssid" name="ssid" value="{ssid}" required>
            
            <label for="password">WiFi Password:</label>
            <input type="password" id="password" name="password" value="{password}" required>
            
            <label for="hostname">Device Hostname:</label>
            <input type="text" id="hostname" name="hostname" value="{hostname}" required>
            
            <button type="submit">Save & Restart</button>
        </form>
    </div>
</body>
</html>
"""
        return html

    def handle_config_save(self, request):
        """Handle configuration save from POST request"""
        try:
            # Extract form data from POST request
            body = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
            params = {}

            for param in body.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    # URL decode
                    value = value.replace("+", " ")
                    # Simple URL decode for common characters
                    value = value.replace("%40", "@")
                    value = value.replace("%21", "!")
                    value = value.replace("%23", "#")
                    value = value.replace("%24", "$")
                    value = value.replace("%25", "%")
                    params[key] = value

            ssid = params.get("ssid", "")
            password = params.get("password", "")
            hostname = params.get("hostname", "wildsensor")

            if ssid and password:
                update_wifi_credentials(ssid, password, hostname)

                response = """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Configuration Saved</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f0f0f0;
        }}
        .success {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 400px;
            margin: 0 auto;
        }}
        h1 {{ color: #28a745; }}
    </style>
</head>
<body>
    <div class="success">
        <h1>✓ Configuration Saved!</h1>
        <p>Device will restart and connect to your WiFi network.</p>
        <p>Please wait 10 seconds...</p>
    </div>
    <script>
        setTimeout(function() {{
            window.location.href = '/';
        }}, 3000);
    </script>
</body>
</html>
"""
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
        self.np.fill((0, 0, 13))
        self.np.write()

        # Serve configuration page
        self.serve_config_page()

        return False


def connect_wifi():
    """Helper function for backward compatibility"""
    manager = WiFiManager()
    return manager.connect()
