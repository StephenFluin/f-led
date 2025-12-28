import network, time

# --- WIFI CONFIGURATION ---
SSID = "FIOT2"
PASSWORD = "Cyborgific@tion"
HOSTNAME = "wildsensor"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Set the hostname BEFORE connecting
    # This ensures the DHCP request includes the name
    try:
        wlan.config(dhcp_hostname=HOSTNAME)
    except Exception as e:
        print(f"Warning: Could not set hostname: {e}")
    
    if not wlan.isconnected():
        print(f"Connecting to {SSID} as '{HOSTNAME}'...")
        wlan.connect(SSID, PASSWORD)
        
        # Wait up to 10 seconds for connection
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            time.sleep(1)
            
    if wlan.isconnected():
        print("Wi-Fi Connected!")
        print(f"IP Address: {wlan.ifconfig()[0]}")
        print(f"Hostname set to: {HOSTNAME}")
    else:
        print("ERROR: Could not connect to Wi-Fi.")

connect_wifi()