"""
Hardware and configuration constants for ESP32 LED Sports Display
Consolidates all hardware pin definitions and magic numbers
"""

# Hardware Pin Definitions
RELAY_PIN = 12
DATA_PIN = 16
BUZZER_PIN = 25
POWER_BUTTON_PIN = 0  # GPIO 0 (common boot button on ESP32)

# LED Configuration
NUM_LEDS = 96

# Brightness Constants (0-100 scale)
DEFAULT_BRIGHTNESS = 50
LOADING_BRIGHTNESS_PERCENT = 5
LOADING_BRIGHTNESS_VALUE = int(255 * LOADING_BRIGHTNESS_PERCENT / 100)  # 13

# Network Configuration
DEFAULT_POLL_INTERVAL = 10  # seconds
NETWORK_CHUNK_SIZE = 256  # bytes
NETWORK_BUFFER_SIZE = 600  # characters

# Power Button Configuration
DEBOUNCE_SEC = 0.3  # seconds

# Goal Celebration
CELEBRATION_DURATION_SEC = 5
HORN_BLAST_COUNT = 3
HORN_BLAST_DURATION_SEC = 1.0
HORN_PAUSE_DURATION_SEC = 0.4

# Buzzer Frequencies
BUZZER_FREQ_1 = 150  # Hz
BUZZER_FREQ_2 = 140  # Hz
BUZZER_DUTY_CYCLE = 512

# Base Colors (RGB at full brightness)
COLOR_GREEN_BASE = (0, 50, 0)
COLOR_RED_BASE = (50, 0, 0)
COLOR_GREEN_CELEBRATION = (0, 255, 0)
COLOR_RED_CELEBRATION = (255, 0, 0)
COLOR_BLUE_AP_MODE = (0, 0, LOADING_BRIGHTNESS_VALUE)

# HTTP Server
DEFAULT_HTTP_PORT = 80

# Access Point Configuration
AP_PASSWORD = "configure"
AP_SSID_PREFIX = "scorebox"

# WiFi Connection
WIFI_CONNECT_TIMEOUT_SEC = 15
WIFI_CHECK_INTERVAL_SEC = 0.1  # Check every 0.1 seconds

# File Paths
CACHE_FILE = "score.txt"
CONFIG_FILE = "config.json"
TEMPLATE_DIR = "/www/"
