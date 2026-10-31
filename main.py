import urequests
import time
import machine, neopixel
import gc
import network
from config import load_config
from power_manager import create_power_manager
import constants

# --- CONFIGURATION ---
config = load_config()
TEAM_ABBREV = config.get("device", {}).get("team_abbrev", "MIN")
POLL_INTERVAL = config.get("device", {}).get(
    "poll_interval", constants.DEFAULT_POLL_INTERVAL
)
BRIGHTNESS = config.get("device", {}).get(
    "brightness", constants.DEFAULT_BRIGHTNESS
)  # 0-100 scale
NUM_LEDS = constants.NUM_LEDS

# Get device identifiers for logging
wlan = network.WLAN(network.STA_IF)
DEVICE_ID = "".join(["{:02x}".format(b) for b in wlan.config("mac")])
HOSTNAME = config.get("wifi", {}).get("hostname", "scorebox-unknown")

# --- PIXEL MAPPING ---
# 0-indexed LED numbers for each point.
# Define the first point for each team manually
## Single panel
# wild_base = [0, 1, 6, 7]
# opp_base = [2, 3, 4, 5]

## Dual Panel
wild_base = [0, 1, 2, 3, 4, 5, 6, 7]
opp_base = [48, 49, 50, 51, 52, 53, 54, 55]

# Initialize the dictionaries with Point 1
WILD_PIXELS = {1: wild_base}
OPP_PIXELS = {1: opp_base}

# Automatically generate Points 2 through 6
# Logic: Each new point is exactly 8 pixels further down the strip
for i in range(2, 7):
    # List comprehension: Take the previous point's pixels and add 8 to each
    WILD_PIXELS[i] = [p + 8 for p in WILD_PIXELS[i - 1]]
    OPP_PIXELS[i] = [p + 8 for p in OPP_PIXELS[i - 1]]

# --- HARDWARE SETUP ---
relay = machine.Pin(constants.RELAY_PIN, machine.Pin.OUT)
relay.on()
time.sleep(0.5)

np = neopixel.NeoPixel(machine.Pin(constants.DATA_PIN), constants.NUM_LEDS)

# Attempt to init buzzer (fails safely if not connected)
buzzer = None
try:
    buzzer = machine.PWM(machine.Pin(constants.BUZZER_PIN))
    buzzer.duty(0)
except:
    pass

# Initialize power manager
power_mgr = create_power_manager(np)
print("Power button ready (press to sleep/wake)")

# --- STATE MANAGEMENT ---
current_wild_score = 0
current_opp_score = 0


def save_cache():
    try:
        with open(constants.CACHE_FILE, "w") as f:
            f.write(f"{current_wild_score},{current_opp_score}")
    except:
        pass


def load_cache():
    global current_wild_score, current_opp_score
    try:
        with open(constants.CACHE_FILE, "r") as f:
            data = f.read().split(",")
            current_wild_score = int(data[0])
            current_opp_score = int(data[1])
            print(f"Loaded Score: {current_wild_score} - {current_opp_score}")
    except:
        print("No cache found, starting at 0-0")
        current_wild_score = 0
        current_opp_score = 0


# --- CORE FUNCTIONS (The Abstractions) ---


def log_event(event_name, event_details=""):
    """
    Log an event to the remote API server.
    event_name: Name of the event (e.g., "device_online", "goal_scored")
    event_details: Optional additional details
    """
    url = f"{constants.API_BASE_URL}/api/log"

    try:
        payload = {
            "deviceId": DEVICE_ID,
            "hostname": HOSTNAME,
            "eventName": event_name,
            "eventDetails": event_details,
        }

        # Convert to JSON string manually (MicroPython may not have json.dumps)
        import ujson

        json_data = ujson.dumps(payload)

        headers = {"Content-Type": "application/json"}
        response = urequests.post(url, data=json_data, headers=headers)

        if response.status_code == 201:
            print(f"Logged event: {event_name}")
        else:
            print(f"Failed to log event: {response.status_code}")

        response.close()
    except Exception as e:
        print(f"Error logging event: {e}")
        # Don't crash if logging fails


def scale_brightness(color, brightness_percent):
    """
    Scale RGB color by brightness percentage (0-100)
    color: tuple of (r, g, b)
    brightness_percent: 0-100
    returns: tuple of (r, g, b) scaled
    """
    scale = brightness_percent / 100.0
    return tuple(int(c * scale) for c in color)


def play_horn():
    """Simulates a hockey horn using the buzzer."""
    if not buzzer:
        print("(No buzzer detected, skipping sound)")
        return

    print("HONK! HONK! HONK!")
    # Three blasts
    for _ in range(constants.HORN_BLAST_COUNT):
        start = time.ticks_ms()
        # Run for 1 second
        while time.ticks_diff(time.ticks_ms(), start) < (
            constants.HORN_BLAST_DURATION_SEC * 1000
        ):
            # Dissonance effect: switch freq rapidly
            buzzer.freq(constants.BUZZER_FREQ_1)
            buzzer.duty(constants.BUZZER_DUTY_CYCLE)
            time.sleep(0.05)
            buzzer.freq(constants.BUZZER_FREQ_2)
            buzzer.duty(constants.BUZZER_DUTY_CYCLE)
            time.sleep(0.05)

        # Pause between blasts
        buzzer.duty(0)
        time.sleep(constants.HORN_PAUSE_DURATION_SEC)


def draw_scoreboard():
    """Updates the static LED matrix based on current scores."""
    np.fill((0, 0, 0))  # Clear

    # Scale base colors by configured brightness
    green = scale_brightness(constants.COLOR_GREEN_BASE, BRIGHTNESS)
    red = scale_brightness(constants.COLOR_RED_BASE, BRIGHTNESS)

    # Draw Wild Points (Green)
    # Loop from 1 to current score
    for i in range(1, current_wild_score + 1):
        pixels = WILD_PIXELS.get(i, [])
        for p in pixels:
            if p < constants.NUM_LEDS:
                np[p] = green

    # Draw Opponent Points (Red)
    for i in range(1, current_opp_score + 1):
        pixels = OPP_PIXELS.get(i, [])
        for p in pixels:
            if p < constants.NUM_LEDS:
                np[p] = red

    np.write()


def trigger_goal(is_wild_goal):
    """
    Runs the full goal celebration.
    is_wild_goal: True for our team (Green), False for enemy (Red)
    """
    # Base celebration color
    base_color = (
        constants.COLOR_GREEN_CELEBRATION
        if is_wild_goal
        else constants.COLOR_RED_CELEBRATION
    )
    # Apply brightness to celebration
    color = scale_brightness(base_color, BRIGHTNESS)
    team_name = TEAM_ABBREV if is_wild_goal else "OPPONENT"

    print(f"\nGOAL FOR {team_name}!")

    # Start Sound (in a non-blocking way if possible, but blocking is fine here)
    if buzzer:
        play_horn()
    else:
        print("No buzzer")

    # Visual Celebration (10 seconds)
    # Pulse effect
    start_time = time.time()
    while (time.time() - start_time) < constants.CELEBRATION_DURATION_SEC:
        # Fade In
        for b in range(0, 150, 25):
            c_scaled = (
                int(color[0] * (b / 255)),
                int(color[1] * (b / 255)),
                int(color[2] * (b / 255)),
            )
            np.fill(c_scaled)
            np.write()
            time.sleep(0.02)
        # Fade Out
        for b in range(150, 0, -25):
            c_scaled = (
                int(color[0] * (b / 255)),
                int(color[1] * (b / 255)),
                int(color[2] * (b / 255)),
            )
            np.fill(c_scaled)
            np.write()
            time.sleep(0.02)

    # Return to scoreboard
    draw_scoreboard()


def manual_set_score(wild, opp):
    """
    TEST FUNCTION: Call this manually to simulate score changes.
    Example: manual_set_score(1, 0) -> Triggers Wild Goal
    """
    global current_wild_score, current_opp_score

    print(
        f"DEBUG: Changing score from {current_wild_score}-{current_opp_score} to {wild}-{opp}"
    )

    # Detect changes
    if wild > current_wild_score:
        trigger_goal(is_wild_goal=True)
    elif opp > current_opp_score:
        trigger_goal(is_wild_goal=False)

    # Update state
    current_wild_score = wild
    current_opp_score = opp

    save_cache()
    draw_scoreboard()
    print("Scoreboard updated.")


def check_network_score():
    """
    Simplified function to check team scores using our API server.
    The API handles all the parsing and caching.
    Returns a tuple: (our_team_score, opponent_score)
    Returns (-1, -1) on network error
    Returns (-2, -2) if team not found
    """
    url = f"{constants.API_BASE_URL}/api/scores/{TEAM_ABBREV}"
    print(f"\nChecking {url} for score updates...")

    gc.collect()  # Clean up memory before network call

    try:
        response = urequests.get(url)

        if response.status_code != 200:
            print(f"API returned status {response.status_code}")
            response.close()
            return (-1, -1)

        # Parse JSON response
        import ujson

        data = ujson.loads(response.text)
        response.close()

        # Check if team was found
        if "status" in data:
            if data["status"] == "not found":
                print(f"Team {TEAM_ABBREV} not playing")
                return (-2, -2)

        # Extract scores
        if "us" in data and "them" in data:
            us_score = data["us"]
            them_score = data["them"]
            print(f"Retrieved scores: {TEAM_ABBREV} {us_score} - {them_score} OPP")
            return (us_score, them_score)

        print("Unexpected API response format")
        return (-1, -1)

    except Exception as e:
        print(f"Network error: {e}")
        return (-1, -1)


# --- MAIN EXECUTION ---
load_cache()
draw_scoreboard()

# Log device startup
try:
    log_event(
        "device_online",
        f"Team: {TEAM_ABBREV}, Score: {current_wild_score}-{current_opp_score}",
    )
except:
    print("Failed to log device startup (continuing anyway)")

# Loop
while True:
    try:
        # Check for power button press
        state_changed = power_mgr.update()

        # If we just woke from sleep, reconnect WiFi
        if state_changed and not power_mgr.is_sleeping:
            print("Reconnecting to WiFi after wake...")
            from wifi_manager import connect_wifi

            connect_wifi()
            draw_scoreboard()  # Restore display

        # Skip normal operations if sleeping
        if power_mgr.is_sleeping:
            time.sleep(1)  # Small sleep to reduce CPU usage
            continue

        debug_mode = False
        if not debug_mode:
            # --- NORMAL OPERATION: Check Network for Score Updates ---
            new_wild_score, new_opp_score = check_network_score()
            if new_wild_score == -1:
                print("Network error occurred, skipping this check.")
            elif new_wild_score == -2:
                print("Team not found in data (not playing?), skipping.")
            else:
                print(
                    f"Retrieved scores: {TEAM_ABBREV} {new_wild_score} - {new_opp_score} OPP"
                )

                if new_wild_score > current_wild_score:
                    trigger_goal(is_wild_goal=True)
                    current_wild_score = new_wild_score
                    current_opp_score = new_opp_score
                    save_cache()
                    draw_scoreboard()
                    # Log the goal
                    try:
                        log_event(
                            "goal_scored",
                            f"{TEAM_ABBREV} goal! Score: {current_wild_score}-{current_opp_score}",
                        )
                    except:
                        print("Failed to log goal event")
                elif new_opp_score > current_opp_score:
                    trigger_goal(is_wild_goal=False)
                    current_wild_score = new_wild_score
                    current_opp_score = new_opp_score
                    save_cache()
                    draw_scoreboard()
                    # Log opponent goal
                    try:
                        log_event(
                            "goal_scored",
                            f"Opponent goal. Score: {current_wild_score}-{current_opp_score}",
                        )
                    except:
                        print("Failed to log goal event")
                else:
                    print("No score change detected.")

            print(f"Waiting {POLL_INTERVAL} seconds until next check...")
            time.sleep(POLL_INTERVAL)
            continue
        else:
            # Testing with manual offline scores
            manual_set_score(0, 0)
            time.sleep(5)
            manual_set_score(1, 0)

            time.sleep(15)
            manual_set_score(1, 1)
            time.sleep(15)
            manual_set_score(2, 1)
            time.sleep(5)
            manual_set_score(3, 1)

            manual_set_score(4, 1)

            manual_set_score(5, 1)

            manual_set_score(6, 1)
            time.sleep(20)

    except KeyboardInterrupt:
        print("\nShutting down...")
        power_mgr.enter_sleep_mode()
        break
