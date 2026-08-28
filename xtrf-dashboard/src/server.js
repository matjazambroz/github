import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  computeAll,
  computeYtdTurnover,
  computeYtdCosts,
  computeYtdPaidTurnover,
  computeYtdPaidCosts,
  computePriorYtdTurnover,
  computePriorYtdCosts,
  computeProjectYtdSummary,
} from "./metrics.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, "..", "public");

const port = Number(process.env.PORT ?? 4173);
const refreshMinutes = Number(process.env.REFRESH_MINUTES ?? 15);
const ytdRefreshMinutes = Number(process.env.YTD_REFRESH_MINUTES ?? 60);

let state = {
  status: "loading",
  data: null,
  error: null,
  lastUpdated: null,
};

let ytdState = {
  status: "loading",
  data: null,
  error: null,
  lastUpdated: null,
};

function errorMessage(err) {
  return err?.status === 401 ? "XTRF API key je neveljaven ali potekel." : err?.message ?? String(err);
}

async function refresh() {
  try {
    const data = await computeAll();
    state = { status: "ok", data, error: null, lastUpdated: new Date().toISOString() };
    console.log(`[${new Date().toLocaleTimeString("sl-SI")}] Refreshed OK`);
  } catch (err) {
    const message = errorMessage(err);
    state = { ...state, status: "error", error: message };
    console.error(`[${new Date().toLocaleTimeString("sl-SI")}] Refresh failed:`, message);
  }
}

// Slower cycle: YTD turnover/costs need to check every invoice issued this
// year (~1000+ calls each, though cached after the first run), so they run
// on their own, less frequent interval instead of blocking/slowing down
// the main 15-minute "today" refresh.
async function refreshYtd() {
  try {
    const [turnover, costs, paidTurnover, paidCosts, priorTurnover, priorCosts, projectSummary] = await Promise.all([
      computeYtdTurnover(),
      computeYtdCosts(),
      computeYtdPaidTurnover(),
      computeYtdPaidCosts(),
      computePriorYtdTurnover(),
      computePriorYtdCosts(),
      computeProjectYtdSummary(),
    ]);
    ytdState = {
      status: "ok",
      data: { turnover, costs, paidTurnover, paidCosts, priorTurnover, priorCosts, projectSummary },
      error: null,
      lastUpdated: new Date().toISOString(),
    };
    console.log(`[${new Date().toLocaleTimeString("sl-SI")}] YTD refreshed OK`);
  } catch (err) {
    const message = errorMessage(err);
    ytdState = { ...ytdState, status: "error", error: message };
    console.error(`[${new Date().toLocaleTimeString("sl-SI")}] YTD refresh failed:`, message);
  }
}

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
};

const server = http.createServer(async (req, res) => {
  if (req.url === "/api/status") {
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ today: state, ytd: ytdState }));
    return;
  }

  const urlPath = req.url === "/" ? "/index.html" : req.url;
  const filePath = path.join(publicDir, urlPath);
  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  try {
    const content = await fs.readFile(filePath);
    const ext = path.extname(filePath);
    res.writeHead(200, {
      "Content-Type": MIME[ext] ?? "application/octet-stream",
      // This dashboard evolves and stays open in a browser for a long time
      // (office TV) - never let stale HTML/JS/CSS get stuck in cache.
      "Cache-Control": "no-store",
    });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
});

server.listen(port, () => {
  console.log(`XTRF Dashboard: http://localhost:${port}`);
  console.log(`Refreshing every ${refreshMinutes} minutes (YTD every ${ytdRefreshMinutes} minutes).`);
});

refresh();
refreshYtd();
setInterval(refresh, refreshMinutes * 60 * 1000);
setInterval(refreshYtd, ytdRefreshMinutes * 60 * 1000);
