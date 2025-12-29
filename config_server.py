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
from template_loader import load_template, render_template, serve_html
from utils import url_decode_params
import constants
import machine


def get_device_code():
    """Get unique device code from MAC address"""
    mac = ubinascii.hexlify(network.WLAN().config("mac")).decode()
    return mac[-4:].upper()


class ConfigServer:
    def __init__(self, port=None):
        if port is None:
            port = constants.DEFAULT_HTTP_PORT
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
        brightness = config.get("device", {}).get("brightness", 50)
        device_code = get_device_code()

        template = load_template("device_config.html")
        html_content = render_template(
            template,
            DEVICE_CODE=device_code,
            SSID=ssid,
            PASSWORD=password,
            HOSTNAME=hostname,
            TEAM=team,
            POLL=poll,
            BRIGHTNESS=brightness,
        )

        return serve_html(html_content)

    def handle_save_device(self, request):
        """Handle device settings save"""
        try:
            body = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
            params = url_decode_params(body)

            config = load_config()

            # Update device settings only
            if "device" not in config:
                config["device"] = {}
            config["device"]["team_abbrev"] = params.get("team", "MIN").upper()
            config["device"]["poll_interval"] = int(params.get("poll", 10))
            config["device"]["brightness"] = int(params.get("brightness", 50))

            save_config(config)

            template = load_template("device_saved.html")
            response = serve_html(template)

            return response

        except Exception as e:
            print(f"Error saving device settings: {e}")
            return f"HTTP/1.1 500 Internal Server Error\r\n\r\nError: {e}"

    def handle_save_wifi(self, request):
        """Handle WiFi settings save"""
        try:
            body = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
            params = url_decode_params(body)

            config = load_config()

            # Update WiFi settings only
            if "wifi" not in config:
                config["wifi"] = {}
            config["wifi"]["ssid"] = params.get("ssid", "")
            config["wifi"]["password"] = params.get("password", "")
            config["wifi"]["hostname"] = params.get("hostname", "wildsensor")

            save_config(config)

            template = load_template("device_saved.html")
            response = serve_html(template)

            return response

        except Exception as e:
            print(f"Error saving WiFi settings: {e}")
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
                elif "POST /save_device" in request:
                    response = self.handle_save_device(request)
                    cl.send(response.encode("utf-8"))
                    cl.close()
                    # Restart after saving
                    import time

                    time.sleep(3)
                    machine.reset()
                    return
                elif "POST /save_wifi" in request:
                    response = self.handle_save_wifi(request)
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
def start_config_server(port=None, background=True):
    """Start the configuration server"""
    if port is None:
        port = constants.DEFAULT_HTTP_PORT
    server = ConfigServer(port)
    if background:
        server.start_background()
    else:
        server.serve()
    return server
