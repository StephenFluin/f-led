import urequests
import time
import machine, neopixel
import gc
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
    Memory-safe function to find both team scores.
    Streams the data instead of loading it all at once.
    Returns a tuple: (our_team_score, opponent_score)
    Returns (-1, -1) on network error
    Returns (-2, -2) if team not found
    """
    url = "https://api-web.nhle.com/v1/score/now"
    print(f"\nChecking {url} for score updates...")

    # Track data for current game being parsed
    away_team_abbrev = None
    away_team_score = None
    home_team_abbrev = None
    home_team_score = None

    # 1. Force cleanup before starting the heavy network op
    gc.collect()

    try:
        # stream=True is CRITICAL. It keeps the data on the network socket
        # instead of downloading it all to RAM.
        response = urequests.get(url, stream=True)

        # We will keep a "rolling window" of text to search through
        buffer = ""

        # Read the stream in small chunks
        while True:
            print("Processing stream chunk")
            chunk = response.raw.read(constants.NETWORK_CHUNK_SIZE)
            if not chunk:
                break

            # Decode chunk to string and add to buffer
            try:
                buffer += chunk.decode("utf-8")
            except:
                continue  # Skip decode errors (rare edge case)

            # Keep buffer small to save RAM
            # But keep enough overlap to catch data split across chunks
            if len(buffer) > constants.NETWORK_BUFFER_SIZE:
                buffer = buffer[-constants.NETWORK_BUFFER_SIZE :]

            # print(f"Checking buffer {buffer}.")

            # SEARCH LOGIC:
            # Look for awayTeam section
            if '"awayTeam"' in buffer and away_team_abbrev is None:
                print("Found awayTeam section")
                away_idx = buffer.find('"awayTeam"')
                away_section = buffer[away_idx : away_idx + 400]

                # Extract abbrev
                if '"abbrev":"' in away_section:
                    abbrev_idx = away_section.find('"abbrev":"')
                    abbrev_start = abbrev_idx + len('"abbrev":"')
                    abbrev_end = away_section.find('"', abbrev_start)
                    away_team_abbrev = away_section[abbrev_start:abbrev_end]

                # Extract score
                if '"score":' in away_section:
                    score_idx = away_section.find('"score":')
                    score_part = away_section[score_idx + len('"score":') :]
                    score_str = ""
                    for char in score_part:
                        if char.isdigit():
                            score_str += char
                        else:
                            break
                    if score_str:
                        away_team_score = int(score_str)
            # else:
            # print(
            #    f"could not find away team data and score in {buffer} and away_team_abbrev is {away_team_abbrev}"
            # )

            # Look for homeTeam section
            if '"homeTeam"' in buffer and home_team_abbrev is None:
                print("Found homeTeam section")

                home_idx = buffer.find('"homeTeam"')
                home_section = buffer[home_idx : home_idx + 400]

                # Extract abbrev
                if '"abbrev":"' in home_section:
                    abbrev_idx = home_section.find('"abbrev":"')
                    abbrev_start = abbrev_idx + len('"abbrev":"')
                    abbrev_end = home_section.find('"', abbrev_start)
                    home_team_abbrev = home_section[abbrev_start:abbrev_end]

                # Extract score
                if '"score":' in home_section:
                    score_idx = home_section.find('"score":')
                    score_part = home_section[score_idx + len('"score":') :]
                    score_str = ""
                    for char in score_part:
                        if char.isdigit():
                            score_str += char
                        else:
                            break
                    if score_str:
                        home_team_score = int(score_str)

            # Check if we've reached the end of a game object ("}]}")
            # This indicates we have all the data for this game
            if "}]}" in buffer:
                # Once we have both teams, check if one is our team
                if (
                    away_team_abbrev
                    and home_team_abbrev
                    and away_team_score is not None
                    and home_team_score is not None
                ):
                    if away_team_abbrev == TEAM_ABBREV:
                        # We're the away team
                        print(
                            f"Found {TEAM_ABBREV} as away team: {away_team_score}-{home_team_score}"
                        )
                        response.close()
                        return (away_team_score, home_team_score)
                    elif home_team_abbrev == TEAM_ABBREV:
                        # We're the home team
                        print(
                            f"Found {TEAM_ABBREV} as home team: {home_team_score}-{away_team_score}"
                        )
                        response.close()
                        return (home_team_score, away_team_score)
                    else:
                        # This game doesn't involve our team
                        print(
                            f"Found game: {away_team_abbrev} vs {home_team_abbrev} - not {TEAM_ABBREV}, continuing..."
                        )

                # Reset for next game - clear buffer and variables
                end_game_idx = buffer.find("}]}")
                if end_game_idx != -1:
                    buffer = buffer[end_game_idx + 3 :]  # Skip past "}]}"

                away_team_abbrev = None
                away_team_score = None
                home_team_abbrev = None
                home_team_score = None

        response.close()

    except Exception as e:
        print(f"Network error: {e}")
        return (-1, -1)

    # If we went through the whole stream and didn't find our team
    return (-2, -2)

    pass


# --- MAIN EXECUTION ---
load_cache()
draw_scoreboard()

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
                elif new_opp_score > current_opp_score:
                    trigger_goal(is_wild_goal=False)
                    current_wild_score = new_wild_score
                    current_opp_score = new_opp_score
                    save_cache()
                    draw_scoreboard()
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
