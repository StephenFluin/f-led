import urequests
import time
import machine, neopixel
import gc

# --- CONFIGURATION ---
TEAM_ABBREV = "MIN"
POLL_INTERVAL = 10
CACHE_FILE = "score.txt"

# Dig2Go Hardware
RELAY_PIN = 12
DATA_PIN = 16
BUZZER_PIN = 25 
NUM_LEDS = 48

# --- PIXEL MAPPING ---
# 0-indexed LED numbers for each point.
# You must fill in the rest of these lists for your specific matrix layout!
WILD_PIXELS = {
    1: [0, 1, 6, 7],      # Point 1
    2: [8,9,14,15],                # Point 2 (Add your pixel IDs here)
    3: [16,17,22,23],                # Point 3
    # ... add more points
}

OPP_PIXELS = {
    1: [2, 3, 4, 5],      # Point 1
    2: [10,11,12,13],                # Point 2
    3: [18,19,20,21],                # Point 3
    # ... add more points
}

# --- HARDWARE SETUP ---
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
relay.on()
time.sleep(0.5)

np = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)

# Attempt to init buzzer (fails safely if not connected)
buzzer = None
try:
    buzzer = machine.PWM(machine.Pin(BUZZER_PIN))
    buzzer.duty(0)
except:
    pass

# --- STATE MANAGEMENT ---
current_wild_score = 0
current_opp_score = 0

def save_cache():
    try:
        with open(CACHE_FILE, "w") as f:
            f.write(f"{current_wild_score},{current_opp_score}")
    except: pass

def load_cache():
    global current_wild_score, current_opp_score
    try:
        with open(CACHE_FILE, "r") as f:
            data = f.read().split(',')
            current_wild_score = int(data[0])
            current_opp_score = int(data[1])
            print(f"Loaded Score: {current_wild_score} - {current_opp_score}")
    except:
        print("No cache found, starting at 0-0")
        current_wild_score = 0
        current_opp_score = 0

# --- CORE FUNCTIONS (The Abstractions) ---

def play_horn():
    """Simulates a hockey horn using the buzzer."""
    if not buzzer: 
        print("(No buzzer detected, skipping sound)")
        return
        
    print("HONK! HONK! HONK!")
    # Three blasts
    for _ in range(3): 
        start = time.ticks_ms()
        # Run for 1 second
        while time.ticks_diff(time.ticks_ms(), start) < 1000:
            # Dissonance effect: switch freq rapidly
            buzzer.freq(150) 
            buzzer.duty(512)
            time.sleep(0.05)
            buzzer.freq(140) 
            buzzer.duty(512)
            time.sleep(0.05)
        
        # Pause between blasts
        buzzer.duty(0)
        time.sleep(0.4)

def draw_scoreboard():
    """Updates the static LED matrix based on current scores."""
    np.fill((0, 0, 0)) # Clear
    
    # Draw Wild Points (Green)
    # Loop from 1 to current score
    for i in range(1, current_wild_score + 1):
        pixels = WILD_PIXELS.get(i, [])
        for p in pixels:
            if p < NUM_LEDS: np[p] = (0, 50, 0)

    # Draw Opponent Points (Red)
    for i in range(1, current_opp_score + 1):
        pixels = OPP_PIXELS.get(i, [])
        for p in pixels:
            if p < NUM_LEDS: np[p] = (50, 0, 0)
            
    np.write()

def trigger_goal(is_wild_goal):
    """
    Runs the full goal celebration.
    is_wild_goal: True for our team (Green), False for enemy (Red)
    """
    color = (0, 255, 0) if is_wild_goal else (255, 0, 0)
    team_name = TEAM_ABBREV if is_wild_goal else "OPPONENT"
    
    print(f"\n🚨 GOAL FOR {team_name}! 🚨")
    
    # Start Sound (in a non-blocking way if possible, but blocking is fine here)
    if buzzer: play_horn()

    # Visual Celebration (10 seconds)
    # Pulse effect
    start_time = time.time()
    while (time.time() - start_time) < 10:
        # Fade In
        for b in range(0, 150, 25):
            c_scaled = (int(color[0]*(b/255)), int(color[1]*(b/255)), int(color[2]*(b/255)))
            np.fill(c_scaled)
            np.write()
            time.sleep(0.02)
        # Fade Out
        for b in range(150, 0, -25):
            c_scaled = (int(color[0]*(b/255)), int(color[1]*(b/255)), int(color[2]*(b/255)))
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
    
    print(f"DEBUG: Changing score from {current_wild_score}-{current_opp_score} to {wild}-{opp}")
    
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

# --- NETWORK LOGIC (Simplified for readability) ---
def check_network_score():
    """
    Memory-safe function to find the score.
    Streams the data instead of loading it all at once.
    """
    url = "https://api-web.nhle.com/v1/score/now"
    score = -1
    found_team = False
    
    # 1. Force cleanup before starting the heavy network op
    gc.collect() 
    
    try:
        # stream=True is CRITICAL. It keeps the data on the network socket 
        # instead of downloading it all to RAM.
        response = urequests.get(url, stream=True)
        
        # We will keep a "rolling window" of text to search through
        buffer = ""
        found_target = False
        
        # Read the stream in small chunks (256 bytes)
        while True:
            chunk = response.raw.read(256)
            if not chunk:
                break
                
            # Decode chunk to string and add to buffer
            try:
                buffer += chunk.decode('utf-8')
            except:
                continue # Skip decode errors (rare edge case)
            
            # Keep buffer small (approx 600 chars) to save RAM
            # But keep enough overlap to catch data split across chunks
            if len(buffer) > 600:
                buffer = buffer[-600:]
            
            # SEARCH LOGIC:
            # We look for our team. The JSON structure usually puts "abbrev" 
            # and "score" close together in the same object.
            # Example: {"abbrev":"MIN", "score":2, ...}
            
            if f'"abbrev":"{TEAM_ABBREV}"' in buffer:
                # We found the Wild! Now look for the score in this same window.
                # We look for the pattern "score":X
                
                # Simple string parsing to find "score": followed by a number
                try:
                    # Find the position of "abbrev":"MIN"
                    team_idx = buffer.find(f'"abbrev":"{TEAM_ABBREV}"')
                    
                    # Look at the text AROUND the team name (before and after)
                    # The score is usually a sibling key
                    snippet = buffer[:] 
                    
                    if '"score":' in snippet:
                        # Extract the number after "score":
                        parts = snippet.split('"score":')
                        # The number is at the start of the second part
                        # e.g., parts[1] starts with "2, ..." or "2}"
                        score_part = parts[1]
                        
                        # Grab digits until we hit a comma or bracket
                        score_str = ""
                        for char in score_part:
                            if char.isdigit():
                                score_str += char
                            else:
                                break
                        
                        if score_str:
                            score = int(score_str)
                            found_team = True
                            break # Stop reading the stream, we got it!
                except Exception as e:
                    print(f"Parsing error: {e}")

        response.close()
        
    except Exception as e:
        print(f"Network error: {e}")
        return -1

    if found_team:
        return score
    else:
        # If we went through the whole stream and didn't find MIN, 
        # they probably aren't playing today.
        return -2 

    pass

# --- MAIN EXECUTION ---
load_cache()
draw_scoreboard()

# Loop
while True:
    try:
        # 1. Listen for User Input via Thonny Shell
        # In Thonny, you can type "manual_set_score(1,0)" in the shell
        # while this loop is sleeping!
        
        # 2. Run Network Check
        manual_set_score(0,0)
        time.sleep(5)
        manual_set_score(1,0)
        
        time.sleep(15) # Short sleep to allow Shell interrupts
        manual_set_score(1,1)
        time.sleep(15)
        manual_set_score(2,1)
        time.sleep(20)
        
    except KeyboardInterrupt:
        break