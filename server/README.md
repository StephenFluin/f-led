# Scorebox Data API

Express-based API server for NHL scorebox data and device logging.

## Features

- **Express 5**: Latest version with improved performance
- **Node.js 22**: Latest LTS with native fetch support
- **TypeScript**: Type-safe development with tsx execution
- **Smart Caching**: Caches entire NHL API response for 3 seconds, reprocesses per team request
- **Event Logging**: Track device events with UTC timestamps
- **Cloud Run Ready**: Optimized for Google Cloud Run deployment

## Development

```bash
npm install
npm run dev
```

Server will run on http://localhost:8484

## Build

For production (optional - tsx can run directly):

```bash
npm run build
npm start
```

Or use tsx directly:

```bash
npx tsx src/index.ts
```

## Docker

```bash
npm run docker:build
npm run docker:run
```

## Deploy to Google Cloud Run

```bash
gcloud run deploy scorebox-data \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## API Endpoints

### GET /api/scores/:team

Get current score for a team (e.g., MIN, CHI, etc.)

Response:

- `{status: 'not found'}` - Team not playing
- `{us: 2, them: 3}` - Team is playing, scores returned

### POST /api/log

Log device events

Body: `{deviceId, hostname, eventName, eventDetails?}`

### GET /api/log

Get all logged events
