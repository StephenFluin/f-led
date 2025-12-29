"""
Example: How to add the configuration server to your main.py
This allows accessing the config interface even when WiFi is connected

Add this code to main.py after WiFi connection is established
"""

# Option 1: Start config server in background (recommended)
# Add this near the top of main.py, after imports
"""
from config_server import start_config_server
import network

# After WiFi is connected (in boot.py), you can get the IP like this:
wlan = network.WLAN(network.STA_IF)
if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"Main app running. Config available at: http://{ip}:8080")
    
    # Start config server on port 8080 (won't interfere with main app)
    config_server = start_config_server(port=8080, background=True)
"""

# Option 2: Manual control
"""
from config_server import ConfigServer

# Create server instance
config_server = ConfigServer(port=8080)

# Start in background thread
config_server.start_background()

# Later, if you need to stop it:
# config_server.stop()
"""

# Example: Full integration in main.py
# Add after the "# --- MAIN EXECUTION ---" section

"""
# =============================================================================
# OPTIONAL: Enable web configuration while running
# =============================================================================
try:
    from config_server import start_config_server
    import network
    
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"\n{'='*50}")
        print(f"Configuration interface available at:")
        print(f"http://{ip}:8080")
        print(f"{'='*50}\n")
        
        # Start in background - won't block main loop
        config_server = start_config_server(port=8080, background=True)
except Exception as e:
    print(f"Config server not started: {e}")
    # Continue anyway - config server is optional

# Your existing main loop continues here
load_cache()
draw_scoreboard()

while True:
    # ... your existing code ...
"""

# Note: The config server runs in a separate thread, so it won't interfere
# with your main application loop. Users can access the config interface
# at any time by visiting http://[device-ip]:8080

# Benefits:
# 1. No need to trigger AP mode to change settings
# 2. Can update team abbreviation during season
# 3. Can adjust poll interval without reflashing
# 4. Can change WiFi without deleting config.json

# Trade-offs:
# - Uses some RAM for the web server thread
# - Opens another port (8080)
# - If RAM is tight, you can skip this and only use AP mode for config
