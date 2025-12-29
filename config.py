"""
Configuration management for ESP32 LED Sports Display
Handles loading/saving WiFi credentials and other settings to a JSON file
"""

import json
import constants

DEFAULT_CONFIG = {
    "wifi": {"ssid": "", "password": "", "hostname": "wildsensor"},
    "device": {
        "team_abbrev": "MIN",
        "poll_interval": constants.DEFAULT_POLL_INTERVAL,
        "brightness": constants.DEFAULT_BRIGHTNESS,
    },
}


def load_config():
    """Load configuration from file, return defaults if not found"""
    try:
        with open(constants.CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("Configuration loaded successfully")
            return config
    except OSError:
        print("No configuration file found, using defaults")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file"""
    try:
        with open(constants.CONFIG_FILE, "w") as f:
            json.dump(config, f)
            print("Configuration saved successfully")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_wifi_credentials():
    """Get WiFi credentials from config"""
    config = load_config()
    return (
        config.get("wifi", {}).get("ssid", ""),
        config.get("wifi", {}).get("password", ""),
        config.get("wifi", {}).get("hostname", "wildsensor"),
    )


def update_wifi_credentials(ssid, password, hostname="wildsensor"):
    """Update WiFi credentials in config"""
    config = load_config()
    if "wifi" not in config:
        config["wifi"] = {}

    config["wifi"]["ssid"] = ssid
    config["wifi"]["password"] = password
    config["wifi"]["hostname"] = hostname

    return save_config(config)
