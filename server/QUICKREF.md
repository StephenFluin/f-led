# Scorebox API Server - Quick Reference

## 🚀 Quick Start

### Development

```bash
cd server
npm install
npm run dev
```

Server runs on http://localhost:8484

### Production Build

```bash
npm run build
npm start
```

### Deploy to Google Cloud Run

```bash
gcloud run deploy scorebox-data \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📡 API Endpoints

| Endpoint            | Method | Description                                 |
| ------------------- | ------ | ------------------------------------------- |
| `/`                 | GET    | API info and available endpoints            |
| `/health`           | GET    | Health check for Cloud Run                  |
| `/api/scores/:team` | GET    | Get current score for team (e.g., MIN, CHI) |
| `/api/log`          | POST   | Log a device event                          |
| `/api/log`          | GET    | Retrieve all logs (optional ?limit=N)       |

## 🎯 Score Response Format

**Team Playing:**

```json
{ "us": 2, "them": 3 }
```

**Team Not Found:**

```json
{ "status": "not found" }
```

## 📝 Logging Format

**POST Request:**

```json
{
  "deviceId": "abc123",
  "hostname": "scorebox-1",
  "eventName": "device_online",
  "eventDetails": "Optional details"
}
```

**Response:**

```json
{
  "success": true,
  "entry": {
    "timestamp": "2025-12-29T12:34:56.789Z",
    "deviceId": "abc123",
    "hostname": "scorebox-1",
    "eventName": "device_online",
    "eventDetails": "Optional details"
  }
}
```

## 🔧 Configuration

### ESP32 Debug Mode

Edit `constants.py`:

```python
DEBUG_MODE = True   # Use local server (http://192.168.1.XXX:8484)
DEBUG_MODE = False  # Use production (https://scorebox-data.fluin.io)
```

### Change Local IP

```python
API_BASE_URL = "http://YOUR_IP:8484" if DEBUG_MODE else "https://scorebox-data.fluin.io"
```

## 🧪 Testing

### Test Script

```bash
cd server
./test-api.sh                                    # Test local
./test-api.sh https://scorebox-data.fluin.io    # Test production
```

### Manual Tests

```bash
# Score check
curl http://localhost:8484/api/scores/MIN

# Log event
curl -X POST http://localhost:8484/api/log \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test","hostname":"test","eventName":"test"}'

# Get logs
curl http://localhost:8484/api/log
```

## 📊 Monitoring

### View Cloud Run Logs

```bash
gcloud run logs tail scorebox-data --region us-central1
```

### Check Service Status

```bash
gcloud run services describe scorebox-data --region us-central1
```

## 🏗️ Project Structure

```
server/
├── src/
│   └── index.ts          # Main Express application
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── Dockerfile            # Container image definition
├── .dockerignore         # Files to exclude from Docker build
├── README.md             # Server documentation
├── DEPLOYMENT.md         # Detailed deployment guide
└── test-api.sh          # API testing script
```

## 💡 Features

- ✅ **Smart Caching:** Entire NHL API response cached for 3 seconds, reprocessed per team request
- ✅ **Node.js 22:** Latest LTS with native fetch (no external HTTP libraries needed)
- ✅ **Express 5:** Latest version with improved performance
- ✅ **TypeScript with tsx:** Direct TypeScript execution, no build step in development
- ✅ **CORS Enabled:** Can be called from browsers
- ✅ **Auto-scaling:** Cloud Run scales based on traffic
- ✅ **Health Checks:** Built-in health endpoint for monitoring
- ✅ **In-Memory Logs:** Fast logging (upgrade to database for persistence)
- ✅ **Error Handling:** Graceful error responses
- ✅ **TypeScript:** Type-safe code

## 🔄 Workflow

1. **ESP32 boots** → Logs "device_online" event
2. **Every 10 seconds** → Fetches `/api/scores/MIN`
3. **Goal detected** → Logs "goal_scored" event
4. **API caches** → Reduces NHL API calls
5. **You monitor** → View logs via `/api/log`

## 📚 Documentation

- **Server Details:** See `server/README.md`
- **Deployment Guide:** See `server/DEPLOYMENT.md`
- **ESP32 Integration:** See `ESP32_API_INTEGRATION.md`

## 🐛 Common Issues

**Server won't start:**

- Run `npm install` first
- Check Node version (need 18+)

**ESP32 can't connect:**

- Verify WiFi connection
- Check API_BASE_URL in constants.py
- Test API in browser first

**Scores not updating:**

- Team might not be playing
- Check team abbreviation (e.g., "MIN" not "Minnesota")
- Test API directly: `curl YOUR_URL/api/scores/MIN`
