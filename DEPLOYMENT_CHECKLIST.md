# Deployment Checklist

Use this checklist to deploy your Scorebox API server and update your ESP32 devices.

## ☁️ Server Deployment

### Prerequisites

- [ ] Google Cloud SDK installed (`gcloud --version`)
- [ ] Authenticated with Google Cloud (`gcloud auth login`)
- [ ] Project selected (`gcloud config set project YOUR_PROJECT_ID`)

### Deploy to Cloud Run

- [ ] Navigate to server directory: `cd server`
- [ ] Install dependencies: `npm install`
- [ ] Test locally: `npm run dev`
- [ ] Test endpoints: `./test-api.sh http://localhost:8484`
- [ ] Deploy to Cloud Run:
  ```bash
  gcloud run deploy scorebox-data \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
  ```
- [ ] Note your service URL from deployment output
- [ ] Test deployed service: `./test-api.sh YOUR_SERVICE_URL`

### Custom Domain (Optional)

- [ ] Map domain to Cloud Run service
- [ ] Add DNS records to domain registrar
- [ ] Wait for SSL certificate provisioning (can take 15-60 min)
- [ ] Test: `curl https://scorebox-data.fluin.io/health`

## 🔧 ESP32 Configuration

### For Production (Cloud Run)

- [ ] Open `constants.py`
- [ ] Set `DEBUG_MODE = False`
- [ ] Verify `API_BASE_URL` production URL is correct
- [ ] Save file

### For Development (Local)

- [ ] Open `constants.py`
- [ ] Set `DEBUG_MODE = True`
- [ ] Find your local IP address:
  - Linux/Mac: `ifconfig` or `ip addr`
  - Windows: `ipconfig`
- [ ] Update IP in `API_BASE_URL` (e.g., `http://192.168.1.100:8484`)
- [ ] Save file
- [ ] Start local server: `cd server && npm run dev`

### Upload to ESP32

- [ ] Connect ESP32 to computer
- [ ] Open your ESP32 IDE (Thonny, ampy, etc.)
- [ ] Upload modified files:
  - [ ] `constants.py`
  - [ ] `main.py`
- [ ] Reset ESP32
- [ ] Open serial monitor

### Verify ESP32 Operation

- [ ] Device connects to WiFi
- [ ] See log message: "Logged event: device_online"
- [ ] See score check: "Checking API for score updates..."
- [ ] See score result: "Retrieved scores: MIN X - Y OPP" or "Team not found"
- [ ] No errors in serial output

## 🧪 Testing

### Test Score Endpoint

```bash
# Should return score or "not found"
curl https://scorebox-data.fluin.io/api/scores/MIN
```

### Test Logging Endpoint

```bash
# Post a test log
curl -X POST https://scorebox-data.fluin.io/api/log \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test","hostname":"test","eventName":"test"}'

# View logs
curl https://scorebox-data.fluin.io/api/log
```

### Check for ESP32 Logs

```bash
# Should see device_online events from your ESP32(s)
curl https://scorebox-data.fluin.io/api/log | grep device_online
```

## 📊 Monitoring

### View Cloud Run Logs

```bash
gcloud run logs tail scorebox-data --region us-central1
```

### Check Service Status

```bash
gcloud run services describe scorebox-data \
  --region us-central1 \
  --format='value(status.conditions[0].message)'
```

### View Recent Logs

```bash
gcloud run logs read scorebox-data \
  --region us-central1 \
  --limit 50
```

## ✅ Success Criteria

You're all set when:

- [ ] API health check returns healthy status
- [ ] Score endpoint returns valid data for your team
- [ ] ESP32 successfully logs "device_online" event
- [ ] ESP32 fetches scores without errors
- [ ] You can see logs at `/api/log` endpoint
- [ ] (During a game) Score updates appear on ESP32
- [ ] (During a game) Goals trigger celebrations
- [ ] (During a game) Goal events appear in logs

## 🐛 Troubleshooting

### Server Issues

- **502/503 errors**: Check Cloud Run logs for crashes
- **CORS errors**: Already configured, check browser console
- **NHL API errors**: Check if NHL API is accessible

### ESP32 Issues

- **Can't reach API**: Check WiFi, verify URL, test in browser
- **Import errors**: Normal for MicroPython modules (network, ujson)
- **Memory errors**: API should reduce these, but check available RAM
- **No score updates**: Check team abbreviation (must be exact, e.g., "MIN")

### Quick Fixes

```bash
# Redeploy server
cd server
gcloud run deploy scorebox-data --source .

# View live logs
gcloud run logs tail scorebox-data --region us-central1

# Test API locally
npm run dev
./test-api.sh
```

## 📝 Notes

- **Caching**: API caches NHL data for 3 seconds (balance between freshness and API limits)
- **Logs**: Currently in-memory (lost on restart). For persistence, add a database.
- **Scaling**: Cloud Run auto-scales. Starts at 0, scales up with traffic.
- **Cost**: Cloud Run has generous free tier. Most hobby use cases are free.
- **Updates**: To update API, just run deploy command again.

## 🎉 Done!

Once all checkboxes are complete, your system is fully operational!

Your ESP32 devices are now:

- ✅ Using the cloud API for simplified score fetching
- ✅ Logging events for monitoring
- ✅ More reliable with less memory usage
- ✅ Ready for future enhancements

Next: Monitor your logs during a game to see it in action! 🏒
