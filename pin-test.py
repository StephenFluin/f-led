import machine, neopixel, time

# Common ESP32 Pins usually safe to use for LEDs
# We skip 1 & 3 (Serial/USB) and 6-11 (Internal Flash)
test_pins = [2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]
NUM_LEDS = 10 # We only need to light a few to test

print("Starting Pin Scanner...")
print("Watch your LED strip. When it flashes GREEN, look at the log here!")
print("-" * 30)

for pin_num in test_pins:
    try:
        # 1. Announce which pin we are testing
        print(f"Testing GPIO {pin_num}...", end="")
        
        # 2. Configure the pin
        pin = machine.Pin(pin_num, machine.Pin.OUT)
        np = neopixel.NeoPixel(pin, NUM_LEDS)
        
        # 3. Try to light it up GREEN
        np.fill((0, 128, 0)) # Green
        np.write()
        time.sleep(0.5) # Keep it on for half a second
        
        # 4. Turn it off (so we know if the next one works)
        np.fill((0, 0, 0))
        np.write()
        
        print(" Done.")
        
    except Exception as e:
        print(f" Error on pin {pin_num}: {e}")
        continue

print("-" * 30)
print("Scan complete. Did you see a flash?")