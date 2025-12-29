"""
Power management for ESP32
Handles power button press to enter/exit sleep mode
"""

import machine
import time
import network
import constants


class PowerManager:
    def __init__(self, led_strip=None):
        """
        Initialize power manager
        led_strip: NeoPixel object to control
        """
        self.led_strip = led_strip
        self.is_sleeping = False
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)

        # Setup power button with pull-up resistor
        # Button press = LOW (0), Released = HIGH (1)
        self.power_button = machine.Pin(
            constants.POWER_BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP
        )

        # Debounce tracking
        self.last_press_time = 0
        self.debounce_sec = constants.DEBOUNCE_SEC

        print(f"Power Manager initialized. Button on GPIO {constants.POWER_BUTTON_PIN}")

    def check_button(self):
        """
        Check if power button was pressed
        Returns True if button was pressed (with debouncing)
        """
        current_time = time.ticks_ms()

        # Button is pressed when value is 0 (active LOW)
        if self.power_button.value() == 0:
            # Check debounce
            if time.ticks_diff(current_time, self.last_press_time) > (
                self.debounce_sec * 1000
            ):
                self.last_press_time = current_time
                return True

        return False

    def enter_sleep_mode(self):
        """Enter low-power sleep mode"""
        if self.is_sleeping:
            return

        print("\n" + "=" * 50)
        print("Entering Sleep Mode")
        print("=" * 50)

        # Turn off LEDs
        if self.led_strip:
            self.led_strip.fill((0, 0, 0))
            self.led_strip.write()
            print("LEDs turned off")

        # Disconnect WiFi
        if self.wlan_sta.isconnected():
            print("Disconnecting WiFi...")
            self.wlan_sta.disconnect()

        # Deactivate WiFi radios to save power
        self.wlan_sta.active(False)
        self.wlan_ap.active(False)
        print("WiFi deactivated")

        self.is_sleeping = True
        print("Sleep mode active. Press power button to wake.")
        print("=" * 50 + "\n")

    def exit_sleep_mode(self):
        """Exit sleep mode and restore normal operation"""
        if not self.is_sleeping:
            return

        print("\n" + "=" * 50)
        print("Waking from Sleep Mode")
        print("=" * 50)

        self.is_sleeping = False

        # Reactivate WiFi
        print("Reactivating WiFi...")
        self.wlan_sta.active(True)

        print("Wake complete. Resuming normal operation.")
        print("=" * 50 + "\n")

        # Return True to signal that WiFi needs reconnection
        return True

    def toggle_power(self):
        """Toggle between sleep and wake modes"""
        if self.is_sleeping:
            return self.exit_sleep_mode()
        else:
            self.enter_sleep_mode()
            return False

    def update(self):
        """
        Call this in your main loop to check for button presses
        Returns True if state changed and WiFi reconnection is needed
        """
        if self.check_button():
            print("Power button pressed!")
            return self.toggle_power()
        return False


def create_power_manager(led_strip):
    """
    Convenience function to create a power manager
    """
    return PowerManager(led_strip)
