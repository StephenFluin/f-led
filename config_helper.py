"""
Helper script to create or update config.json
Can be run on the ESP32 or used to generate a config file to upload
"""

import json


def create_config_file(
    ssid="",
    password="",
    hostname="wildsensor",
    team_abbrev="MIN",
    poll_interval=10,
    num_leds=48,
):
    """Create a new configuration file"""

    config = {
        "wifi": {"ssid": ssid, "password": password, "hostname": hostname},
        "device": {
            "team_abbrev": team_abbrev,
            "poll_interval": poll_interval,
            "num_leds": num_leds,
        },
    }

    try:
        with open("config.json", "w") as f:
            json.dump(config, f)
        print("Configuration file created successfully!")
        print(json.dumps(config, indent=2))
        return True
    except Exception as e:
        print(f"Error creating config file: {e}")
        return False


def update_wifi(ssid, password, hostname="wildsensor"):
    """Update just the WiFi settings"""
    try:
        # Load existing config
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except:
            config = {
                "wifi": {},
                "device": {"team_abbrev": "MIN", "poll_interval": 10, "num_leds": 48},
            }

        # Update WiFi settings
        config["wifi"]["ssid"] = ssid
        config["wifi"]["password"] = password
        config["wifi"]["hostname"] = hostname

        # Save
        with open("config.json", "w") as f:
            json.dump(config, f)

        print("WiFi configuration updated!")
        return True
    except Exception as e:
        print(f"Error updating WiFi config: {e}")
        return False


def update_team(team_abbrev):
    """Update the team abbreviation"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        config["device"]["team_abbrev"] = team_abbrev

        with open("config.json", "w") as f:
            json.dump(config, f)

        print(f"Team updated to: {team_abbrev}")
        return True
    except Exception as e:
        print(f"Error updating team: {e}")
        return False


def show_config():
    """Display current configuration"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        print("Current Configuration:")
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"Error reading config: {e}")


# Example usage (uncomment to use):
# create_config_file(ssid="MyWiFi", password="MyPassword")
# update_wifi("NewNetwork", "NewPassword")
# update_team("CHI")  # Change to Chicago
# show_config()
