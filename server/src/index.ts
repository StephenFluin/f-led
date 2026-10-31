import express, { Request, Response } from "express";
import cors from "cors";

const app = express();
const PORT = process.env.PORT || 8484;

// Middleware
app.use(cors());
app.use(express.json());

// ==================== SCORE CACHING ====================
interface NHLApiCache {
  data: any;
  timestamp: number;
}

let nhlApiCache: NHLApiCache | null = null;
const CACHE_TTL_MS = 3000; // 3 seconds

interface TeamScore {
  abbrev: string;
  score: number;
}

interface GameData {
  awayTeam: TeamScore;
  homeTeam: TeamScore;
}

/**
 * Fetch the entire NHL API response and cache it
 */
async function fetchNHLData(): Promise<any> {
  // Check cache first
  if (nhlApiCache && Date.now() - nhlApiCache.timestamp < CACHE_TTL_MS) {
    console.log("NHL API cache hit");
    return nhlApiCache.data;
  }

  console.log("Fetching fresh NHL API data");

  try {
    const response = await fetch("https://api-web.nhle.com/v1/score/now");
    if (!response.ok) {
      throw new Error(`NHL API returned ${response.status}`);
    }

    const data = await response.json();

    // Cache the entire response
    nhlApiCache = {
      data,
      timestamp: Date.now(),
    };

    return data;
  } catch (error) {
    console.error("Error fetching NHL data:", error);
    throw error;
  }
}

/**
 * Find team score from cached NHL data
 */
function findTeamScore(
  nhlData: any,
  teamAbbrev: string
): { us: number; them: number } | { status: string } {
  const cacheKey = teamAbbrev.toUpperCase();

  // Find game with our team
  if (!nhlData.games || !Array.isArray(nhlData.games)) {
    return { status: "not found" };
  }

  for (const game of nhlData.games) {
    const awayTeam = game.awayTeam?.abbrev;
    const homeTeam = game.homeTeam?.abbrev;
    const awayScore = game.awayTeam?.score ?? 0;
    const homeScore = game.homeTeam?.score ?? 0;

    if (awayTeam === cacheKey) {
      // Our team is away
      return { us: awayScore, them: homeScore };
    } else if (homeTeam === cacheKey) {
      // Our team is home
      return { us: homeScore, them: awayScore };
    }
  }

  // Team not found in any game
  return { status: "not found" };
}

// ==================== LOGGING ====================
interface LogEntry {
  timestamp: string;
  deviceId: string;
  hostname: string;
  eventName: string;
  eventDetails?: string;
}

// In-memory log storage (use a database in production)
const logs: LogEntry[] = [];

// ==================== ROUTES ====================

/**
 * GET /api/scores/:team
 * Get current score for a team
 */
app.get("/api/scores/:team", async (req: Request, res: Response) => {
  try {
    const team = req.params.team.toUpperCase();
    console.log(`Score request for team: ${team}`);

    // Fetch (or get from cache) the full NHL data
    const nhlData = await fetchNHLData();

    // Process the data for the requested team
    const result = findTeamScore(nhlData, team);

    res.json(result);
  } catch (error) {
    console.error("Error in /api/scores/:team:", error);
    res.status(500).json({ error: "Failed to fetch score data" });
  }
});

/**
 * POST /api/log
 * Log a device event
 */
app.post("/api/log", (req: Request, res: Response) => {
  try {
    const { deviceId, hostname, eventName, eventDetails } = req.body;

    // Validate required fields
    if (!deviceId || !hostname || !eventName) {
      return res.status(400).json({
        error: "Missing required fields: deviceId, hostname, eventName",
      });
    }

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      deviceId,
      hostname,
      eventName,
      eventDetails: eventDetails || undefined,
    };

    logs.push(logEntry);
    console.log("New log entry:", logEntry);

    res.status(201).json({ success: true, entry: logEntry });
  } catch (error) {
    console.error("Error in POST /api/log:", error);
    res.status(500).json({ error: "Failed to log event" });
  }
});

/**
 * GET /api/log
 * Retrieve all log entries
 */
app.get("/api/log", (req: Request, res: Response) => {
  try {
    // Optional: Add pagination or filtering
    const limit = req.query.limit
      ? parseInt(req.query.limit as string)
      : undefined;

    const result = limit ? logs.slice(-limit) : logs;

    res.json({
      count: result.length,
      logs: result,
    });
  } catch (error) {
    console.error("Error in GET /api/log:", error);
    res.status(500).json({ error: "Failed to retrieve logs" });
  }
});

/**
 * GET /health
 * Health check endpoint for Cloud Run
 */
app.get("/health", (req: Request, res: Response) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

/**
 * GET /
 * Root endpoint
 */
app.get("/", (req: Request, res: Response) => {
  res.json({
    name: "Scorebox Data API",
    version: "1.0.0",
    endpoints: {
      scores: "/api/scores/:team",
      log_post: "POST /api/log",
      log_get: "GET /api/log",
      health: "/health",
    },
  });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`🚀 Scorebox Data API running on port ${PORT}`);
  console.log(`   Environment: ${process.env.NODE_ENV || "development"}`);
  console.log(`   Health check: http://localhost:${PORT}/health`);
});

// Error handling for server
server.on("error", (error: NodeJS.ErrnoException) => {
  if (error.code === "EADDRINUSE") {
    console.error(`❌ Error: Port ${PORT} is already in use`);
  } else if (error.code === "EACCES") {
    console.error(`❌ Error: Permission denied to use port ${PORT}`);
  } else {
    console.error(`❌ Server error:`, error);
  }
  process.exit(1);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("SIGTERM signal received: closing HTTP server");
  server.close(() => {
    console.log("HTTP server closed");
  });
});

export default app;
