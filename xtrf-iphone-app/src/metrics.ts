import { xtrfRequest, type XtrfEnv } from "./xtrfClient";
import { dateOnlyToEpochMs, todayDateString, mondayOfThisWeek, todayParts } from "./dateUtils";
import { combineIntoEur, getCachedInvoice, putCachedInvoice, type InvoiceCacheEntry } from "./cache";

type CacheEnv = XtrfEnv & { CACHE: KVNamespace; XTRF_TIMEZONE: string };

interface ProjectDetail {
  status?: string;
  finance?: { currencyId?: number; totalAgreed?: number };
  dates?: { actualStartDate?: { time: number }; startDate?: { time: number } };
}

interface InvoiceDetail {
  currencyId?: number;
  totalNetto?: number;
  status?: string;
  dates?: { invoiceDate?: { time: number } };
}

function addToTotals(totals: Record<string, number>, currencyId: number, amount: number) {
  totals[currencyId] = (totals[currencyId] ?? 0) + amount;
}

export interface AmountResult {
  amount: number;
  count: number;
}

// Fetches each project touched since the start of this week once, then
// classifies it into "today" and/or "this week" buckets by actualStartDate
// (falling back to startDate) - one project-detail fetch serves both
// figures instead of two separate passes.
async function computeProjectTurnover(env: CacheEnv): Promise<{ day: AmountResult; week: AmountResult }> {
  const timeZone = env.XTRF_TIMEZONE;
  const today = todayDateString(timeZone);
  const dayStartMs = dateOnlyToEpochMs(today, timeZone);
  const dayEndMs = dayStartMs + 24 * 60 * 60 * 1000;
  const weekStartMs = dateOnlyToEpochMs(mondayOfThisWeek(timeZone), timeZone);

  const projectIds = await xtrfRequest<number[]>(env, "GET", "/projects/ids", { updatedSince: weekStartMs });

  const dayTotals: Record<string, number> = {};
  const dayCounts: Record<string, number> = {};
  const weekTotals: Record<string, number> = {};
  const weekCounts: Record<string, number> = {};

  for (const id of projectIds) {
    const project = await xtrfRequest<ProjectDetail>(env, "GET", `/projects/${id}`);
    const currencyId = project?.finance?.currencyId;
    const totalAgreed = project?.finance?.totalAgreed;
    const startedMs = project?.dates?.actualStartDate?.time ?? project?.dates?.startDate?.time;
    if (currencyId === undefined || typeof totalAgreed !== "number" || typeof startedMs !== "number") {
      continue;
    }
    if (startedMs >= weekStartMs && startedMs < dayEndMs) {
      addToTotals(weekTotals, currencyId, totalAgreed);
      weekCounts[currencyId] = (weekCounts[currencyId] ?? 0) + 1;
      if (startedMs >= dayStartMs) {
        addToTotals(dayTotals, currencyId, totalAgreed);
        dayCounts[currencyId] = (dayCounts[currencyId] ?? 0) + 1;
      }
    }
  }

  const [day, week] = await Promise.all([
    combineIntoEur(env, dayTotals, dayCounts),
    combineIntoEur(env, weekTotals, weekCounts),
  ]);
  return { day, week };
}

// This year, Jan 1 through the end of today (matches xtrf-dashboard's
// invoice-based YTD turnover).
function currentYtdRange(timeZone: string): { year: number; startMs: number; endMs: number } {
  const { year, month, day } = todayParts(timeZone);
  return {
    year,
    startMs: dateOnlyToEpochMs(`${year}-01-01`, timeZone),
    endMs: dateOnlyToEpochMs(`${year}-${month}-${day}`, timeZone) + 24 * 60 * 60 * 1000,
  };
}

export interface YtdResult extends AmountResult {
  year: number;
  syncing: boolean;
  cachedInvoices: number;
  totalInvoiceCandidates: number;
}

// Client-invoice turnover (totalNetto, status SENT, dates.invoiceDate this
// year). Each invoice's financials are permanently cached in KV once fetched
// (an issued invoice's amount/date/status don't change again), so only
// invoices not yet in the cache count against `maxFetchPerRun` - the first
// few scheduled runs backfill the cache in bounded batches (to stay under
// the Workers per-invocation subrequest limit); every run after that is
// just `count(candidates) - count(cached)` new fetches, i.e. cheap.
async function computeYtdTurnover(env: CacheEnv, maxFetchPerRun: number): Promise<YtdResult> {
  const { year, startMs, endMs } = currentYtdRange(env.XTRF_TIMEZONE);
  const invoiceIds = await xtrfRequest<number[]>(env, "GET", "/accounting/customers/invoices/ids", {
    updatedSince: startMs,
  });

  const totals: Record<string, number> = {};
  const counts: Record<string, number> = {};
  let cachedCount = 0;
  let fetchedThisRun = 0;

  for (const id of invoiceIds) {
    let entry = await getCachedInvoice(env, id);
    if (entry && entry.status !== undefined) {
      cachedCount++;
    } else if (fetchedThisRun < maxFetchPerRun) {
      const invoice = await xtrfRequest<InvoiceDetail>(env, "GET", `/accounting/customers/invoices/${id}`);
      entry = {
        currencyId: invoice?.currencyId,
        totalNetto: invoice?.totalNetto,
        dateMs: invoice?.dates?.invoiceDate?.time ?? null,
        status: invoice?.status,
      };
      await putCachedInvoice(env, id, entry);
      fetchedThisRun++;
      cachedCount++;
    } else {
      // Budget exhausted for this run - picked up on a later scheduled run.
      continue;
    }

    const { currencyId, totalNetto, dateMs, status } = entry as InvoiceCacheEntry;
    if (currencyId === undefined || typeof totalNetto !== "number") {
      continue;
    }
    if (typeof dateMs !== "number" || dateMs < startMs || dateMs >= endMs) {
      continue;
    }
    if (status !== "SENT") {
      continue;
    }
    addToTotals(totals, currencyId, totalNetto);
    counts[currencyId] = (counts[currencyId] ?? 0) + 1;
  }

  const combined = await combineIntoEur(env, totals, counts);
  return {
    ...combined,
    year,
    syncing: cachedCount < invoiceIds.length,
    cachedInvoices: cachedCount,
    totalInvoiceCandidates: invoiceIds.length,
  };
}

export interface AllMetrics {
  generatedAt: string;
  day: AmountResult;
  week: AmountResult;
  ytd: YtdResult;
}

export async function computeAll(env: CacheEnv, maxInvoicesPerRun: number): Promise<AllMetrics> {
  const [{ day, week }, ytd] = await Promise.all([computeProjectTurnover(env), computeYtdTurnover(env, maxInvoicesPerRun)]);
  return { generatedAt: new Date().toISOString(), day, week, ytd };
}
