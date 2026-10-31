# ESP32 Integration Guide

## Overview

The ESP32 device now communicates with the API server for two main purposes:

1. **Fetching scores** - Gets simplified, pre-parsed score data
2. **Logging events** - Reports device status and game events

## API Endpoints Used

### 1. GET /api/scores/:team

**Purpose:** Get current game score for a specific team

**Example Request:**

```
GET https://scorebox-data.fluin.io/api/scores/MIN
```

**Example Responses:**

Team is playing:

```json
{
  "us": 2,
  "them": 3
}
```

Team not found (not playing today):

```json
{
  "status": "not found"
}
```

### 2. POST /api/log

**Purpose:** Log device events

**Example Request:**

```json
POST https://scorebox-data.fluin.io/api/log
Content-Type: application/json

{
  "deviceId": "a1b2c3d4e5f6",
  "hostname": "scorebox-living-room",
  "eventName": "device_online",
  "eventDetails": "Team: MIN, Score: 0-0"
}
```

**Example Response:**

```json
{
  "success": true,
  "entry": {
    "timestamp": "2025-12-29T12:34:56.789Z",
    "deviceId": "a1b2c3d4e5f6",
    "hostname": "scorebox-living-room",
    "eventName": "device_online",
    "eventDetails": "Team: MIN, Score: 0-0"
  }
}
```

### 3. GET /api/log

**Purpose:** Retrieve all logged events

**Example Request:**

```
GET https://scorebox-data.fluin.io/api/log?limit=10
```

**Example Response:**

```json
{
  "count": 2,
  "logs": [
    {
      "timestamp": "2025-12-29T12:34:56.789Z",
      "deviceId": "a1b2c3d4e5f6",
      "hostname": "scorebox-living-room",
      "eventName": "device_online",
      "eventDetails": "Team: MIN, Score: 0-0"
    },
    {
      "timestamp": "2025-12-29T13:45:23.456Z",
      "deviceId": "a1b2c3d4e5f6",
      "hostname": "scorebox-living-room",
      "eventName": "goal_scored",
      "eventDetails": "MIN goal! Score: 1-0"
    }
  ]
}
```

## Code Changes in ESP32

### constants.py

Added API configuration with debug/production modes:

```python
# API Configuration
DEBUG_MODE = False  # Change to True for local testing
API_BASE_URL = "http://192.168.1.100:8484" if DEBUG_MODE else "https://scorebox-data.fluin.io"
```

### main.py

**New Function: `log_event()`**

```python
def log_event(event_name, event_details=""):
    """Log an event to the remote API server."""
    # Sends device info and event to API
    # Safe to call - won't crash if network fails
```

**Updated Function: `check_network_score()`**

- Now uses the simplified API endpoint
- Much less memory usage (no streaming/parsing needed)
- Faster and more reliable
- Returns same format: `(our_score, opponent_score)`

**Event Logging:**
The device logs:

1. **On startup:** Reports when device comes online with current score
2. **On team goal:** Reports when your team scores
3. **On opponent goal:** Reports when opponent scores

## Benefits

### For the ESP32:

- ✅ **Less memory usage** - No complex JSON parsing on device
- ✅ **Faster processing** - API does the heavy lifting
- ✅ **Better reliability** - Simpler code = fewer bugs
- ✅ **Easier debugging** - Can see device events in logs

### For You:

- ✅ **Monitor devices** - See when devices are online/offline
- ✅ **Track events** - Know when goals happen across all your devices
- ✅ **Centralized caching** - API caches NHL data, reduces API calls
- ✅ **Future features** - Easy to add notifications, stats, etc.

## Testing

### Test Score Fetching:

```python
# In main.py, set debug_mode = False and run
# Watch serial output for:
# "Checking https://scorebox-data.fluin.io/api/scores/MIN for score updates..."
# "Retrieved scores: MIN 2 - 3 OPP"
```

### Test Event Logging:

```python
# Device should log on startup automatically
# Check logs via:
# curl https://scorebox-data.fluin.io/api/log
```

### Local Development Testing:

1. Set `DEBUG_MODE = True` in constants.py
2. Update local IP in constants.py
3. Run server: `cd server && npm run dev`
4. Deploy to ESP32 and test

## Troubleshooting

### Device can't reach API:

- Check WiFi connection
- Verify API_BASE_URL is correct
- Test URL in browser: `https://scorebox-data.fluin.io/health`
- Check serial output for error messages

### Scores not updating:

- Check if team is actually playing today
- Verify TEAM_ABBREV is correct (e.g., "MIN" not "Minnesota")
- Check API directly: `curl https://scorebox-data.fluin.io/api/scores/MIN`

### Events not logging:

- Non-critical - device will continue working
- Check network connectivity
- Verify API is deployed and running
- Check Cloud Run logs for errors
