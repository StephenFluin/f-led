import machine, neopixel, time

# --- DIG2GO CONFIGURATION ---
RELAY_PIN = 12   # The "Safety Switch" that powers the strip
DATA_PIN = 16    # The actual LED data line
NUM_LEDS = 48

def run_dig2go_test():
    print("1. Initializing Dig2Go Power Relay...")
    # Configure the power pin and turn it ON
    power_switch = machine.Pin(RELAY_PIN, machine.Pin.OUT)
    power_switch.on() 
    
    # Wait a moment for the power to stabilize
    time.sleep(0.5) 
    print("   Power is ON.")

    print(f"2. Setting up {NUM_LEDS} LEDs on GPIO {DATA_PIN}...")
    np = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)

    while True:
        # Red
        print("   Color: RED")
        np.fill((50, 0, 0))
        np.write()
        time.sleep(1)

        # Green
        print("   Color: GREEN")
        np.fill((0, 50, 0))
        np.write()
        time.sleep(1)

        # Blue
        print("   Color: BLUE")
        np.fill((0, 0, 50))
        np.write()
        time.sleep(1)
        
        # Off (Blink)
        np.fill((0, 0, 0))
        np.write()
        time.sleep(0.5)

# Run the test
try:
    run_dig2go_test()
except KeyboardInterrupt:
    print("\nTest stopped. Turning off LED power...")
    # Optional: Cut power to the strip when you stop the script
    machine.Pin(RELAY_PIN, machine.Pin.OUT).off()