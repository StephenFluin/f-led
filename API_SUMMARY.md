# Scorebox Data API - Project Summary

This update adds a cloud-based API server to simplify score fetching and enable device monitoring for your ESP32 LED scoreboard.

## 📦 What Was Created

### Server (New `/server` folder)

A complete Express/TypeScript API server ready for Google Cloud Run:

```
server/
├── src/index.ts          # Express app with all endpoints
├── package.json          # Dependencies & build scripts
├── tsconfig.json         # TypeScript config
├── Dockerfile            # Cloud Run deployment
├── .dockerignore         # Docker exclusions
├── README.md             # Server overview
├── DEPLOYMENT.md         # Deployment instructions
├── QUICKREF.md           # Quick reference guide
└── test-api.sh          # Testing script
```

### ESP32 Updates

Modified your existing ESP32 code:

- **constants.py**: Added `DEBUG_MODE` and `API_BASE_URL` configuration
- **main.py**:
  - New `log_event()` function for remote logging
  - Simplified `check_network_score()` using new API
  - Logs sent on device startup and when goals are scored
  - Device ID and hostname tracking

### Documentation

- **ESP32_API_INTEGRATION.md**: Guide for ESP32 integration
- **API_SUMMARY.md**: This file

## 🎯 Key Features

### 1. Score API (`/api/scores/:team`)

**Before:** ESP32 parsed large NHL JSON response (memory intensive)
**Now:** API does the parsing, returns minimal response

```javascript
// Response when team is playing:
{"us": 2, "them": 3}

// Response when team not found:
{"status": "not found"}
```

**Benefits:**

- 3-second caching reduces NHL API calls
- Much less memory usage on ESP32
- Faster, more reliable

### 2. Event Logging (`/api/log`)

Track what's happening across all your devices:

```javascript
POST /api/log
{
  "deviceId": "unique-mac-address",
  "hostname": "scorebox-living-room",
  "eventName": "device_online",
  "eventDetails": "Team: MIN, Score: 0-0"
}
```

**Events Logged:**

- Device comes online
- Team scores a goal
- Opponent scores a goal

**View logs:**

```bash
curl https://scorebox-data.fluin.io/api/log
```

## 🚀 Getting Started

### 1. Set Up Server Locally (for testing)

```bash
cd server
npm install
npm run dev
```

Server runs on http://localhost:8484

Test it:

```bash
./test-api.sh
```

### 2. Deploy to Google Cloud Run

```bash
cd server
gcloud run deploy scorebox-data \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

Then set up your custom domain (scorebox-data.fluin.io) following `server/DEPLOYMENT.md`

### 3. Configure ESP32

**For production (default):**

```python
# In constants.py:
DEBUG_MODE = False  # Uses https://scorebox-data.fluin.io
```

**For local development:**

```python
# In constants.py:
DEBUG_MODE = True  # Uses http://192.168.1.XXX:8484
# Update the IP address to match your computer
```

Upload to ESP32 and watch it connect!

## 📊 How It Works

```
                    ┌─────────────────────────────────┐
                    │      NHL Public API             │
                    │  api-web.nhle.com/v1/score/now  │
                    └─────────────┬───────────────────┘
                                  │
                                  │ (Large JSON, all games)
                                  │
                    ┌─────────────▼───────────────────┐
                    │   Your API Server               │
                    │   (Cloud Run / Local)           │
                    │                                 │
                    │  • Fetches NHL data             │
                    │  • Parses & filters for team    │
                    │  • Caches for 3 seconds         │
                    │  • Returns minimal JSON         │
                    │  • Logs device events           │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  API Endpoints                  │
                    │                                 │
                    │  GET /api/scores/MIN            │
                    │    → {"us": 2, "them": 3}       │
                    │                                 │
                    │  POST /api/log                  │
                    │    ← device events              │
                    │                                 │
                    │  GET /api/log                   │
                    │    → all logged events          │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  ESP32 Scoreboard(s)            │
                    │                                 │
                    │  • Fetches every 10 sec         │
                    │  • Low memory usage             │
                    │  • Logs startup & goals         │
                    │  • Updates LED display          │
                    └─────────────────────────────────┘
```

### Data Flow

1. **NHL API** → Raw game data (all teams, all games)
2. **Your API Server** → Parses, filters, caches
3. **ESP32 Devices** → Simple GET request
4. **API Response** → Tiny JSON: `{"us": 2, "them": 3}`
5. **ESP32** → Updates LEDs, celebrates goals
6. **ESP32** → Logs events back to API
7. **You** → Monitor all devices via `/api/log`

## 🔧 Configuration Modes

### Production Mode (`DEBUG_MODE = False`)

- ESP32 → https://scorebox-data.fluin.io
- Requires internet connection
- API hosted on Google Cloud Run
- Auto-scaling, always available

### Debug Mode (`DEBUG_MODE = True`)

- ESP32 → http://YOUR_LOCAL_IP:8484
- Works on local network only
- Run server with `npm run dev`
- Good for testing without deploying

## 📝 API Endpoints Reference

| Endpoint            | Method | Purpose                      |
| ------------------- | ------ | ---------------------------- |
| `/`                 | GET    | API info                     |
| `/health`           | GET    | Health check                 |
| `/api/scores/MIN`   | GET    | Get Minnesota Wild score     |
| `/api/scores/CHI`   | GET    | Get Chicago Blackhawks score |
| `/api/log`          | POST   | Log device event             |
| `/api/log?limit=10` | GET    | Get last 10 log entries      |

## 🧪 Testing

### Test the Server

```bash
cd server

# Local testing
npm run dev
./test-api.sh

# Production testing
./test-api.sh https://scorebox-data.fluin.io
```

### Test from ESP32

1. Set `DEBUG_MODE = True` in constants.py
2. Update local IP address
3. Start local server: `npm run dev`
4. Upload code to ESP32
5. Watch serial monitor for:
   - "Checking http://192.168.1.XXX:8484/api/scores/MIN..."
   - "Logged event: device_online"
   - Score updates

## 📚 Documentation Files

- **server/README.md** - Server overview
- **server/DEPLOYMENT.md** - Detailed deployment guide
- **server/QUICKREF.md** - Quick reference
- **ESP32_API_INTEGRATION.md** - ESP32 integration guide
- **API_SUMMARY.md** - This file

## 💡 Next Steps

1. **Deploy the server** to Google Cloud Run
2. **Set up custom domain** (scorebox-data.fluin.io)
3. **Update ESP32** with production settings
4. **Monitor logs** to see your devices in action
5. **Optional:** Add database for persistent logs (see DEPLOYMENT.md)

## 🎁 Benefits

### For Your ESP32

- ✅ Less memory usage
- ✅ Simpler code
- ✅ Faster score updates
- ✅ More reliable

### For You

- ✅ Monitor all devices
- ✅ See real-time events
- ✅ Centralized caching
- ✅ Foundation for future features (notifications, stats, etc.)

## ❓ Need Help?

Check these files:

- Setup issues → `server/DEPLOYMENT.md`
- API usage → `server/QUICKREF.md`
- ESP32 integration → `ESP32_API_INTEGRATION.md`
- Testing → Run `server/test-api.sh`

## 🎉 You're All Set!

The server is ready to deploy, and your ESP32 code is ready to use it. Happy scoring! 🏒
