# Deployment Guide for Scorebox Data API

## Technology Stack

- **Node.js 22**: Latest LTS with native fetch support
- **Express 5**: Latest version with improved performance
- **TypeScript**: Type-safe development, executed via tsx
- **Smart Caching**: Entire NHL API response cached for 3 seconds, reprocessed per team

## Local Development

1. **Install dependencies:**

   ```bash
   cd server
   npm install
   ```

2. **Run in development mode:**

   ```bash
   npm run dev
   ```

   Server will be available at http://localhost:8484

3. **Test the endpoints:**

   ```bash
   # Test score endpoint
   curl http://localhost:8484/api/scores/MIN

   # Test logging
   curl -X POST http://localhost:8484/api/log \
     -H "Content-Type: application/json" \
     -d '{"deviceId":"test123","hostname":"test-device","eventName":"test_event","eventDetails":"Testing"}'

   # Get logs
   curl http://localhost:8484/api/log
   ```

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud SDK installed (`gcloud`)
- Authenticated with Google Cloud: `gcloud auth login`
- Project set: `gcloud config set project YOUR_PROJECT_ID`

### Deploy

1. **From the server directory:**

   ```bash
   cd server

   gcloud run deploy scorebox-data \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8484
   ```

2. **Get your service URL:**

   ```bash
   gcloud run services describe scorebox-data \
     --region us-central1 \
     --format 'value(status.url)'
   ```

3. **Set up custom domain (scorebox-data.fluin.io):**

   a. Map the domain:

   ```bash
   gcloud run domain-mappings create \
     --service scorebox-data \
     --domain scorebox-data.fluin.io \
     --region us-central1
   ```

   b. Get the DNS records to add:

   ```bash
   gcloud run domain-mappings describe \
     --domain scorebox-data.fluin.io \
     --region us-central1
   ```

   c. Add the provided DNS records to your domain registrar

### Update Deployment

To deploy updates:

```bash
cd server
gcloud run deploy scorebox-data \
  --source . \
  --platform managed \
  --region us-central1
```

## ESP32 Configuration

### For Production (using scorebox-data.fluin.io):

In `constants.py`:

```python
DEBUG_MODE = False
```

### For Development (using local server):

1. Find your computer's local IP address:

   - Linux/Mac: `ifconfig` or `ip addr`
   - Windows: `ipconfig`

2. Update `constants.py`:

   ```python
   DEBUG_MODE = True
   API_BASE_URL = "http://192.168.1.XXX:8484" if DEBUG_MODE else "https://scorebox-data.fluin.io"
   ```

   Replace `192.168.1.XXX` with your actual local IP

3. Make sure your ESP32 is on the same network

## Monitoring

### View logs:

```bash
gcloud run logs read scorebox-data \
  --region us-central1 \
  --limit 50
```

### View service status:

```bash
gcloud run services describe scorebox-data \
  --region us-central1
```

## Troubleshooting

### Test the deployed service:

```bash
# Replace with your actual service URL
SERVICE_URL="https://scorebox-data-XXXXXXXX.run.app"

# Test score endpoint
curl $SERVICE_URL/api/scores/MIN

# Test health
curl $SERVICE_URL/health
```

### Check Cloud Run logs:

```bash
gcloud run logs tail scorebox-data --region us-central1
```

## Notes

- **Caching Strategy**: The entire NHL API response is cached for 3 seconds. Each team request reprocesses the cached data, meaning multiple teams can be queried without additional API calls during the cache window.
- **In-Memory Storage**: Logs are stored in-memory. For persistent storage, consider adding Cloud Firestore or Cloud SQL.
- **Auto-Scaling**: Cloud Run auto-scales based on traffic and scales to zero when idle.
- **Native Fetch**: Uses Node.js 22's native fetch API (no external dependencies).
- **TypeScript Execution**: Uses tsx to run TypeScript directly without a build step in development.
