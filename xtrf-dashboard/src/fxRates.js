import fs from "node:fs/promises";
import zlib from "node:zlib";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.join(__dirname, "..", "data");
const cachePath = path.join(dataDir, "ecb-rates.csv");
// The plain .csv at the same path has been seen serving a stale, corrupt copy,
// so the .zip is used and the result is sanity-checked in isValid().
const ECB_URL = process.env.ECB_RATES_URL ?? "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip";
const MAX_AGE_MS = 24 * 60 * 60 * 1000;

// Historical EUR reference rates from the ECB (units of currency per 1 EUR,
// one row per working day). Used to convert foreign-currency invoices at the
// rate of their invoice date - which is how XTRF's own reports convert them -
// instead of one current rate for the whole year. XTRF's API only exposes
// today's rate, so there is no way to get the historical one from it.
let table = null; // { dates: sorted ["YYYY-MM-DD"], rates: Map<date, Record<iso, number>> }
let loading = null;

function parse(csv) {
  const lines = csv.trim().split(/\r?\n/);
  const head = lines[0].split(",").map((h) => h.trim());
  const rates = new Map();
  for (const line of lines.slice(1)) {
    const cells = line.split(",");
    const row = {};
    for (let i = 1; i < head.length; i++) {
      const v = parseFloat(cells[i]);
      if (head[i] && Number.isFinite(v)) {
        row[head[i]] = v;
      }
    }
    rates.set(cells[0].trim(), row);
  }
  return { dates: [...rates.keys()].sort(), rates };
}

async function readCache() {
  try {
    const stat = await fs.stat(cachePath);
    return { csv: await fs.readFile(cachePath, "utf-8"), ageMs: Date.now() - stat.mtimeMs };
  } catch {
    return null;
  }
}

// Minimal reader for a single-file .zip (deflate), so no dependency is needed.
function unzipFirstFile(buf) {
  let eocd = buf.length - 22;
  while (eocd >= 0 && buf.readUInt32LE(eocd) !== 0x06054b50) {
    eocd--;
  }
  if (eocd < 0) {
    throw new Error("not a zip file");
  }
  const central = buf.readUInt32LE(eocd + 16);
  const method = buf.readUInt16LE(central + 10);
  const compressedSize = buf.readUInt32LE(central + 20);
  const localOffset = buf.readUInt32LE(central + 42);
  const dataStart = localOffset + 30 + buf.readUInt16LE(localOffset + 26) + buf.readUInt16LE(localOffset + 28);
  const data = buf.subarray(dataStart, dataStart + compressedSize);
  return (method === 8 ? zlib.inflateRawSync(data) : data).toString("utf-8");
}

// A usable table has USD/GBP, goes back years and is no more than ~2 weeks
// old (the ECB publishes every working day).
function isValid(csv) {
  if (!csv.startsWith("Date,")) {
    return false;
  }
  const { dates, rates } = parse(csv);
  const newest = dates.at(-1);
  const fresh = newest && Date.now() - Date.parse(newest) < 14 * 24 * 60 * 60 * 1000;
  return Boolean(fresh && dates[0] < "2005-01-01" && rates.get(newest)?.USD > 0.5 && rates.get(newest)?.GBP > 0.3);
}

async function download() {
  const response = await fetch(ECB_URL);
  if (!response.ok) {
    throw new Error(`ECB rates request failed: ${response.status}`);
  }
  const body = Buffer.from(await response.arrayBuffer());
  const csv = ECB_URL.endsWith(".zip") ? unzipFirstFile(body) : body.toString("utf-8");
  if (!isValid(csv)) {
    throw new Error("ECB rates response is not a current, valid rates table");
  }
  await fs.mkdir(dataDir, { recursive: true });
  await fs.writeFile(cachePath, csv);
  return csv;
}

async function load() {
  const cached = await readCache();
  if (cached && cached.ageMs < MAX_AGE_MS && isValid(cached.csv)) {
    return parse(cached.csv);
  }
  try {
    return parse(await download());
  } catch (err) {
    console.error("ECB rates unavailable:", err.message);
    // An older but valid file is still far better than the current-rate fallback.
    return cached && isValid(cached.csv) ? parse(cached.csv) : null;
  }
}

function ensureLoaded() {
  if (table) {
    return Promise.resolve(table);
  }
  loading ??= load().then((t) => {
    table = t;
    loading = null;
    // Re-check after a day so a long-running dashboard picks up new rates.
    setTimeout(() => (table = null), MAX_AGE_MS).unref();
    return t;
  });
  return loading;
}

function localDate(ms, timeZone) {
  return new Intl.DateTimeFormat("en-CA", { timeZone }).format(new Date(ms));
}

// Units of `isoCode` per 1 EUR on the last working day on or before `dateMs`
// (local calendar date in `timeZone`), or null if the ECB has no such rate.
export async function ecbRateAt(isoCode, dateMs, timeZone) {
  if (isoCode === "EUR") {
    return 1;
  }
  const t = await ensureLoaded();
  if (!t) {
    return null;
  }
  const day = localDate(dateMs, timeZone);
  let lo = 0;
  let hi = t.dates.length - 1;
  let found = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (t.dates[mid] <= day) {
      found = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  // CSV is newest-first but dates is sorted ascending, so `found` is the
  // last working day on or before `day`. Walk back over blank cells.
  for (let i = found; i >= 0 && i > found - 10; i--) {
    const rate = t.rates.get(t.dates[i])?.[isoCode];
    if (rate) {
      return rate;
    }
  }
  return null;
}
