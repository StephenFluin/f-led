"""
Optional: Run a persistent configuration web server
This allows reconfiguration even when connected to WiFi
Can be imported and started from main.py if desired
"""

import socket
import _thread
import network
import ubinascii
from config import (
    get_wifi_credentials,
    update_wifi_credentials,
    load_config,
    save_config,
)
import machine


def get_device_code():
    """Get unique device code from MAC address"""
    mac = ubinascii.hexlify(network.WLAN().config("mac")).decode()
    return mac[-4:].upper()


class ConfigServer:
    def __init__(self, port=8080):
        self.port = port
        self.running = False

    def get_config_page(self):
        """Generate the configuration page"""
        config = load_config()
        ssid = config.get("wifi", {}).get("ssid", "")
        password = config.get("wifi", {}).get("password", "")
        hostname = config.get("wifi", {}).get("hostname", "wildsensor")
        team = config.get("device", {}).get("team_abbrev", "MIN")
        poll = config.get("device", {}).get("poll_interval", 10)
        leds = config.get("device", {}).get("num_leds", 48)
        device_code = get_device_code()

        html = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ScoreBox Configuration</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
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
            margin-bottom: 10px;
        }}
        h2 {{
            color: #555;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        label {{
            display: block;
            margin: 15px 0 5px 0;
            color: #555;
            font-weight: bold;
        }}
        input, select {{
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
        .section {{
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏒 ScoreBox {device_code}</h1>
        <div class="info">
            Device Configuration Panel - Changes require restart
        </div>
        
        <form action="/save" method="POST">
            <h2>WiFi Settings</h2>
            <div class="section">
                <label for="ssid">WiFi Network (SSID):</label>
                <input type="text" id="ssid" name="ssid" value="{ssid}" required>
                
                <label for="password">WiFi Password:</label>
                <input type="password" id="password" name="password" value="{password}" required>
                
                <label for="hostname">Device Hostname:</label>
                <input type="text" id="hostname" name="hostname" value="{hostname}" required>
            </div>
            
            <h2>Device Settings</h2>
            <div class="section">
                <label for="team">Team Abbreviation:</label>
                <input type="text" id="team" name="team" value="{team}" maxlength="3" required>
                
                <label for="poll">Poll Interval (seconds):</label>
                <input type="number" id="poll" name="poll" value="{poll}" min="5" max="300" required>
                
                <label for="leds">Number of LEDs:</label>
                <input type="number" id="leds" name="leds" value="{leds}" min="1" max="300" required>
            </div>
            
            <button type="submit">Save & Restart</button>
        </form>
    </div>
</body>
</html>
"""
        return html

    def handle_save(self, request):
        """Handle configuration save"""
        try:
            body = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
            params = {}

            for param in body.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    value = value.replace("+", " ")
                    value = value.replace("%40", "@")
                    value = value.replace("%21", "!")
                    value = value.replace("%23", "#")
                    value = value.replace("%24", "$")
                    value = value.replace("%25", "%")
                    params[key] = value

            config = load_config()

            # Update WiFi settings
            if "wifi" not in config:
                config["wifi"] = {}
            config["wifi"]["ssid"] = params.get("ssid", "")
            config["wifi"]["password"] = params.get("password", "")
            config["wifi"]["hostname"] = params.get("hostname", "wildsensor")

            # Update device settings
            if "device" not in config:
                config["device"] = {}
            config["device"]["team_abbrev"] = params.get("team", "MIN").upper()
            config["device"]["poll_interval"] = int(params.get("poll", 10))
            config["device"]["num_leds"] = int(params.get("leds", 48))

            save_config(config)

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
        <p>Device will restart in 3 seconds...</p>
    </div>
</body>
</html>
"""
            return response

        except Exception as e:
            print(f"Error saving: {e}")
            return f"HTTP/1.1 500 Internal Server Error\r\n\r\nError: {e}"

    def serve(self):
        """Start the web server"""
        addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)

        print(f"Configuration server running on port {self.port}")
        self.running = True

        while self.running:
            try:
                cl, addr = s.accept()
                request = cl.recv(1024).decode("utf-8")

                if "GET / " in request or "GET /config" in request:
                    response = self.get_config_page()
                elif "POST /save" in request:
                    response = self.handle_save(request)
                    cl.send(response.encode("utf-8"))
                    cl.close()
                    # Restart after saving
                    import time

                    time.sleep(3)
                    machine.reset()
                    return
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

                cl.send(response.encode("utf-8"))
                cl.close()

            except Exception as e:
                print(f"Server error: {e}")
                try:
                    cl.close()
                except:
                    pass

        s.close()

    def start_background(self):
        """Start server in background thread"""
        try:
            _thread.start_new_thread(self.serve, ())
            print(f"Config server started in background on port {self.port}")
        except Exception as e:
            print(f"Could not start background server: {e}")

    def stop(self):
        """Stop the server"""
        self.running = False


# Convenience function
def start_config_server(port=8080, background=True):
    """Start the configuration server"""
    server = ConfigServer(port)
    if background:
        server.start_background()
    else:
        server.serve()
    return server
