# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ESP32 BOOT SEQUENCE                       │
└─────────────────────────────────────────────────────────────────┘

Power On
   │
   ├─> boot.py executes
   │      │
   │      ├─> Import wifi_manager
   │      │      │
   │      │      ├─> WiFiManager.__init__()
   │      │      │      └─> Setup NeoPixel for spinner
   │      │      │
   │      │      └─> connect()
   │      │             │
   │      │             ├─> Load config.json
   │      │             │      ├─> File exists? → Use credentials
   │      │             │      └─> File missing? → Empty SSID
   │      │             │
   │      │             ├─> try_connect_sta()
   │      │             │      │
   │      │             │      ├─> Enable Station Mode
   │      │             │      ├─> Set hostname
   │      │             │      ├─> Begin connection
   │      │             │      │
   │      │             │      └─> Wait up to 15 seconds
   │      │             │             │
   │      │             │             ├─> Show loading spinner
   │      │             │             │   (Blue @ 5% brightness)
   │      │             │             │   Cycles through LEDs
   │      │             │             │   Updates every 0.1s
   │      │             │             │
   │      │             │             ├─> Connected?
   │      │             │             │      │
   │      │             │             │      ├─> YES ✓
   │      │             │             │      │   ├─> Clear LEDs
   │      │             │             │      │   ├─> Print IP
   │      │             │             │      │   └─> Return True
   │      │             │             │      │
   │      │             │             │      └─> NO ✗
   │      │             │             │          └─> Return False
   │      │             │             │
   │      │             │             └─> Timeout reached
   │      │             │
   │      │             └─> Connection failed?
   │      │                    │
   │      │                    └─> start_access_point()
   │      │                           │
   │      │                           ├─> Enable AP mode
   │      │                           │   SSID: ESP32-Config
   │      │                           │   Pass: configure
   │      │                           │   IP: 192.168.4.1
   │      │                           │
   │      │                           ├─> Set LEDs to solid blue
   │      │                           │   (5% brightness)
   │      │                           │
   │      │                           └─> serve_config_page()
   │      │                                  │
   │      │                                  └─> HTTP Server on :80
   │      │                                      │
   │      │                                      ├─> GET / → HTML form
   │      │                                      │
   │      │                                      └─> POST /save
   │      │                                          ├─> Parse form data
   │      │                                          ├─> Save config.json
   │      │                                          ├─> Send success page
   │      │                                          └─> machine.reset()
   │      │
   │      └─> WiFi connected!
   │
   └─> main.py executes
          │
          ├─> Load config.json
          │      └─> Get TEAM_ABBREV, POLL_INTERVAL, NUM_LEDS
          │
          ├─> Initialize hardware
          │      ├─> NeoPixel strip
          │      ├─> Buzzer
          │      └─> Relay
          │
          ├─> Load cached score
          │
          ├─> Draw scoreboard
          │
          └─> Main loop
                 ├─> Poll NHL API
                 ├─> Detect score changes
                 ├─> Trigger goal celebrations
                 └─> Update LEDs


┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION WEB FLOW                        │
└─────────────────────────────────────────────────────────────────┘

User connects to scorebox-XXXX
   │
   ├─> Opens browser: http://192.168.4.1
   │      │
   │      └─> GET / request
   │             │
   │             └─> Server responds with HTML form
   │                    │
   │                    ├─> WiFi SSID input
   │                    ├─> WiFi Password input
   │                    ├─> Hostname input
   │                    ├─> Team abbreviation input
   │                    ├─> Poll interval input
   │                    ├─> Number of LEDs input
   │                    └─> Submit button
   │
   ├─> User fills form and clicks "Save & Restart"
   │      │
   │      └─> POST /save request
   │             │
   │             ├─> Parse URL-encoded form data
   │             │
   │             ├─> Update config dictionary
   │             │      ├─> wifi.ssid
   │             │      ├─> wifi.password
   │             │      ├─> wifi.hostname
   │             │      ├─> device.team_abbrev
   │             │      ├─> device.poll_interval
   │             │      └─> device.num_leds
   │             │
   │             ├─> Save to config.json
   │             │
   │             ├─> Send success page
   │             │
   │             └─> Wait 3 seconds
   │                    │
   │                    └─> machine.reset()
   │
   └─> Device restarts with new config


┌─────────────────────────────────────────────────────────────────┐
│                       LED STATUS INDICATORS                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬────────────────┬──────────┬─────────────────┐
│ State            │ Pattern        │ Color    │ Brightness      │
├──────────────────┼────────────────┼──────────┼─────────────────┤
│ WiFi Connecting  │ Rotating       │ Blue     │ 5% (13/255)     │
│                  │ Single LED     │          │                 │
│                  │ 100ms/LED      │          │                 │
├──────────────────┼────────────────┼──────────┼─────────────────┤
│ AP Mode Active   │ Solid Fill     │ Blue     │ 5% (13/255)     │
│                  │ All LEDs       │          │                 │
├──────────────────┼────────────────┼──────────┼─────────────────┤
│ Connected/Idle   │ Off            │ Black    │ 0%              │
├──────────────────┼────────────────┼──────────┼─────────────────┤
│ Displaying Score │ Static Points  │ Green/   │ ~20% (50/255)   │
│                  │                │ Red      │                 │
├──────────────────┼────────────────┼──────────┼─────────────────┤
│ Goal Celebration │ Pulsing        │ Green or │ 0-60%           │
│                  │ Fade in/out    │ Red      │ (0-150/255)     │
└──────────────────┴────────────────┴──────────┴─────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                        FILE STRUCTURE                            │
└─────────────────────────────────────────────────────────────────┘

ESP32 Filesystem:
│
├── boot.py                  (WiFi connection on startup)
│
├── main.py                  (Main application logic)
│
├── config.py                (Config file management)
│
├── wifi_manager.py          (WiFi + AP + Web server)
│
├── config_server.py         (Optional: Runtime config server)
│
├── config_helper.py         (Optional: Config utilities)
│
├── test_wifi.py            (Optional: Testing utilities)
│
├── config.json             (Generated: Device configuration)
│   └── {
│       "wifi": {
│           "ssid": "...",
│           "password": "...",
│           "hostname": "..."
│       },
│       "device": {
│           "team_abbrev": "...",
│           "poll_interval": ...,
│           "num_leds": ...
│       }
│   }
│
└── score.txt               (Generated: Score cache)


┌─────────────────────────────────────────────────────────────────┐
│                       NETWORK TOPOLOGY                           │
└─────────────────────────────────────────────────────────────────┘

MODE 1: Station Mode (Normal Operation)
┌──────────────┐
│ Home Router  │
│ 192.168.x.x  │
└──────┬───────┘
       │
       │ WiFi Connection
       │
┌──────▼────────────┐
│   ESP32 Device    │
│  (Station Mode)   │
│  192.168.x.xxx    │ ──┐
│  hostname: set    │   │
└───────────────────┘   │
                        │ Polls NHL API
                        │
                   ┌────▼─────────┐
                   │  Internet    │
                   │  NHL API     │
                   └──────────────┘


MODE 2: Access Point Mode (Configuration)
┌──────────────────┐
│  ESP32 Device    │
│  (AP Mode)       │
│  192.168.4.1     │
│  SSID:           │
│  scorebox-XXXX   │
└────────┬─────────┘
         │
         │ Direct WiFi
         │ Connection
         │
┌────────▼─────────┐
│   User Phone/    │
│   Laptop         │
│   192.168.4.x    │
│                  │
│   Browser:       │
│   192.168.4.1:80 │
└──────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      MEMORY CONSIDERATIONS                       │
└─────────────────────────────────────────────────────────────────┘

ESP32 RAM: ~520KB total, ~160KB available for Python

Memory Usage Estimate:
├── MicroPython Runtime     ~200KB
├── WiFi Stack              ~50KB
├── HTTP Server             ~20KB
├── NeoPixel Buffer         ~150 bytes (48 LEDs × 3 bytes)
├── Application Code        ~30KB
├── Config/Cache Files      ~1KB
└── Free for operations     ~50-100KB

Optimization Strategies:
├── Stream HTTP responses (don't load full page in RAM)
├── Parse JSON incrementally (NHL API response)
├── Garbage collect before network operations
├── Use small buffers (256-600 bytes)
└── Reuse socket connections where possible
```
