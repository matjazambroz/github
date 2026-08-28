import { xtrfRequest } from "./xtrfClient.js";
import { dateOnlyToEpochMs, todayDateString } from "./dateUtils.js";
import { createInvoiceCache } from "./invoiceCache.js";

const timeZone = process.env.XTRF_TIMEZONE ?? "Europe/Ljubljana";

const clientInvoiceCache = createInvoiceCache("invoice-cache.json");
const vendorInvoiceCache = createInvoiceCache("vendor-invoice-cache.json");
const projectCache = createInvoiceCache("project-cache.json");

const currencyCache = new Map();
const exchangeRateCache = new Map();

async function resolveCurrency(currencyId) {
  if (currencyCache.has(currencyId)) {
    return currencyCache.get(currencyId);
  }
  const currency = await xtrfRequest("GET", `/dictionaries/currency/${currencyId}`);
  const isoCode = currency?.isoCode ?? `#${currencyId}`;
  currencyCache.set(currencyId, isoCode);
  return isoCode;
}

// XTRF's base/default currency is EUR. GET /dictionaries/currency/{isoCode}/exchangeRate
// returns how many units of that currency equal 1 EUR (e.g. USD ~1.165), sourced from
// OpenExchangeRates.org. So converting to EUR is: amount / exchangeRate.
async function resolveEurExchangeRate(isoCode) {
  if (isoCode === "EUR") {
    return { rate: 1, date: null };
  }
  if (exchangeRateCache.has(isoCode)) {
    return exchangeRateCache.get(isoCode);
  }
  const data = await xtrfRequest("GET", `/dictionaries/currency/${isoCode}/exchangeRate`);
  const rate = parseFloat(data?.exchangeRate);
  const dateMs = data?.publicationDate?.time ?? data?.dateFrom?.time;
  const result = { rate, date: dateMs ? new Date(dateMs).toISOString() : null };
  exchangeRateCache.set(isoCode, result);
  return result;
}

function addToTotals(totals, currencyId, amount) {
  totals[currencyId] = (totals[currencyId] ?? 0) + amount;
}

// Combines per-currency totals (keyed by currencyId) into a single EUR
// amount using XTRF's own exchange rates, plus which rates were used.
async function combineIntoEur(totalsByCurrencyId, counts) {
  let totalEur = 0;
  let totalCount = 0;
  const rates = [];
  for (const [currencyId, amount] of Object.entries(totalsByCurrencyId)) {
    const code = await resolveCurrency(currencyId);
    const { rate, date } = await resolveEurExchangeRate(code);
    totalEur += rate ? amount / rate : amount;
    totalCount += counts[currencyId] ?? 0;
    if (code !== "EUR") {
      rates.push({ code, rate, date });
    }
  }
  return { amount: totalEur, count: totalCount, rates };
}

async function totalsByCurrencyCode(totalsByCurrencyId, counts) {
  const result = {};
  for (const [currencyId, amount] of Object.entries(totalsByCurrencyId)) {
    const code = await resolveCurrency(currencyId);
    result[code] = { amount, count: counts[currencyId] ?? 0 };
  }
  return result;
}

// "Turnover" for a date range - projects have no real "Added on"/creation
// date via the Home API, so `updatedSince` alone hugely overcounts (it
// catches ANY project touched in the window, including old high-value
// projects merely edited today). `actualStartDate` (when work actually
// began) is a much closer real-world proxy: candidates are fetched via
// updatedSince=startMs (cheap, bounds the set), then filtered to
// actualStartDate actually falling in [startMs, endMs) (falling back to
// startDate if actualStartDate is unset).
async function computeTotalAgreedTotalsForRange(startMs, endMs) {
  const projectIds = await xtrfRequest("GET", "/projects/ids", { updatedSince: startMs });

  const totals = {};
  const counts = {};
  for (const id of projectIds) {
    const project = await xtrfRequest("GET", `/projects/${id}`);
    const currencyId = project?.finance?.currencyId;
    const totalAgreed = project?.finance?.totalAgreed;
    const startedMs = project?.dates?.actualStartDate?.time ?? project?.dates?.startDate?.time;
    if (currencyId === undefined || typeof totalAgreed !== "number") {
      continue;
    }
    if (typeof startedMs !== "number" || startedMs < startMs || startedMs >= endMs) {
      continue;
    }
    addToTotals(totals, currencyId, totalAgreed);
    counts[currencyId] = (counts[currencyId] ?? 0) + 1;
  }

  return { totals, counts };
}

export async function computeTotalAgreedToday() {
  const today = todayDateString(timeZone);
  const dayStartMs = dateOnlyToEpochMs(today, timeZone);
  const dayEndMs = dayStartMs + 24 * 60 * 60 * 1000;
  const { totals, counts } = await computeTotalAgreedTotalsForRange(dayStartMs, dayEndMs);
  return totalsByCurrencyCode(totals, counts);
}

// Monday (ISO week start) of the current week, as a "YYYY-MM-DD" string.
function mondayOfThisWeek() {
  const { year, month, day } = todayParts();
  const asUtc = new Date(Date.UTC(year, Number(month) - 1, Number(day)));
  const daysSinceMonday = (asUtc.getUTCDay() + 6) % 7; // getUTCDay: Sun=0..Sat=6 -> Mon=0
  asUtc.setUTCDate(asUtc.getUTCDate() - daysSinceMonday);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "UTC" }).format(asUtc);
}

// Unlike the daily card, weekly turnover is combined into a single EUR
// total (via XTRF's own exchange rates) instead of one card per currency.
export async function computeTotalAgreedThisWeek() {
  const today = todayDateString(timeZone);
  const weekStartMs = dateOnlyToEpochMs(mondayOfThisWeek(), timeZone);
  const dayEndMs = dateOnlyToEpochMs(today, timeZone) + 24 * 60 * 60 * 1000;
  const { totals, counts } = await computeTotalAgreedTotalsForRange(weekStartMs, dayEndMs);
  const combined = await combineIntoEur(totals, counts);
  return { totals: { EUR: { amount: combined.amount, count: combined.count } }, rates: combined.rates };
}

async function computePaidInvoicesForRange(startMs, endMs) {
  const invoiceIds = await xtrfRequest("GET", "/accounting/customers/invoices/ids", { updatedSince: startMs });

  const totals = {};
  const counts = {};
  for (const id of invoiceIds) {
    const payments = await xtrfRequest("GET", `/accounting/customers/invoices/${id}/payments`);
    const paymentsInRange = Array.isArray(payments)
      ? payments.filter((p) => {
          const t = p?.paymentDate?.time;
          return typeof t === "number" && t >= startMs && t < endMs;
        })
      : [];
    if (paymentsInRange.length === 0) {
      continue;
    }

    const invoice = await xtrfRequest("GET", `/accounting/customers/invoices/${id}`);
    const currencyId = invoice?.currencyId;
    if (currencyId === undefined) {
      continue;
    }
    const sum = paymentsInRange.reduce((acc, p) => acc + (p.amount ?? 0), 0);
    addToTotals(totals, currencyId, sum);
    counts[currencyId] = (counts[currencyId] ?? 0) + 1;
  }

  const combined = await combineIntoEur(totals, counts);
  return { totals: { EUR: { amount: combined.amount, count: combined.count } }, rates: combined.rates };
}

export async function computePaidInvoicesToday() {
  const today = todayDateString(timeZone);
  const dayStartMs = dateOnlyToEpochMs(today, timeZone);
  const dayEndMs = dayStartMs + 24 * 60 * 60 * 1000;
  return computePaidInvoicesForRange(dayStartMs, dayEndMs);
}

export async function computePaidInvoicesThisWeek() {
  const today = todayDateString(timeZone);
  const weekStartMs = dateOnlyToEpochMs(mondayOfThisWeek(), timeZone);
  const dayEndMs = dateOnlyToEpochMs(today, timeZone) + 24 * 60 * 60 * 1000;
  return computePaidInvoicesForRange(weekStartMs, dayEndMs);
}

// Shared date-range-from-invoices logic (used for client "turnover" and
// vendor "costs", both this year and the same period last year). Once
// issued, an invoice's currencyId/totalNetto/date never change (payments/
// status updates don't touch them), so each invoice only ever needs to be
// fetched once - cached indefinitely after that, across all callers/years
// (the cache is keyed by invoice id, not by range). Candidates are fetched
// via updatedSince=startMs (an invoice's creation counts as a modification,
// so this doesn't miss any invoice actually dated in-range), then filtered
// to startMs <= dateMs < endMs to drop invoices outside the requested
// range that were merely touched during the fetch window (e.g. paid).
async function computeRangeFromInvoices({
  listPath,
  invoicePath,
  cache,
  extractDateMs,
  startMs,
  endMs,
  label,
  requireStatus,
}) {
  const invoiceIds = await xtrfRequest("GET", listPath, { updatedSince: startMs });

  await cache.load();
  let cacheHits = 0;

  const totals = {};
  const counts = {};
  for (const id of invoiceIds) {
    let entry = cache.get(id);
    // Cache entries must have `status` cached (older entries from before
    // this field existed don't) to be usable as a hit here.
    if (entry && entry.status !== undefined) {
      cacheHits++;
    } else {
      const invoice = await xtrfRequest("GET", invoicePath(id));
      entry = {
        ...entry,
        currencyId: invoice?.currencyId,
        totalNetto: invoice?.totalNetto,
        totalGross: invoice?.totalGross,
        dateMs: extractDateMs(invoice),
        status: invoice?.status,
      };
      cache.set(id, entry);
    }

    const { currencyId, totalNetto, dateMs, status } = entry;
    if (currencyId === undefined || typeof totalNetto !== "number") {
      continue;
    }
    if (typeof dateMs !== "number" || dateMs < startMs || dateMs >= endMs) {
      continue;
    }
    if (requireStatus && status !== requireStatus) {
      continue;
    }
    addToTotals(totals, currencyId, totalNetto);
    counts[currencyId] = (counts[currencyId] ?? 0) + 1;
  }

  await cache.saveIfDirty();
  console.log(`${label}: ${invoiceIds.length} invoices, ${cacheHits} from cache, ${invoiceIds.length - cacheHits} fetched.`);

  return combineIntoEur(totals, counts);
}

// This year, Jan 1 through the end of today.
function currentYtdRange() {
  const { year, month, day } = todayParts();
  return {
    year,
    startMs: dateOnlyToEpochMs(`${year}-01-01`, timeZone),
    endMs: dateOnlyToEpochMs(`${year}-${month}-${day}`, timeZone) + 24 * 60 * 60 * 1000,
  };
}

// Same period last year: Jan 1 through the same calendar day, one year back
// - a fair YoY comparison against currentYtdRange().
function priorYtdRange() {
  const { year, month, day } = todayParts();
  const priorYear = year - 1;
  return {
    year: priorYear,
    startMs: dateOnlyToEpochMs(`${priorYear}-01-01`, timeZone),
    endMs: dateOnlyToEpochMs(`${priorYear}-${month}-${day}`, timeZone) + 24 * 60 * 60 * 1000,
  };
}

function todayParts() {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" })
    .formatToParts(new Date())
    .reduce((acc, p) => ({ ...acc, [p.type]: p.value }), {});
  return { year: Number(parts.year), month: parts.month, day: parts.day };
}

async function computeTurnoverForRange({ year, startMs, endMs }) {
  const combined = await computeRangeFromInvoices({
    listPath: "/accounting/customers/invoices/ids",
    invoicePath: (id) => `/accounting/customers/invoices/${id}`,
    cache: clientInvoiceCache,
    extractDateMs: (invoice) => invoice?.dates?.invoiceDate?.time ?? null,
    startMs,
    endMs,
    label: `Promet ${year}`,
    requireStatus: "SENT",
  });
  return { year, amount: combined.amount, count: combined.count, rates: combined.rates };
}

async function computeCostsForRange({ year, startMs, endMs }) {
  const combined = await computeRangeFromInvoices({
    listPath: "/accounting/providers/invoices/ids",
    invoicePath: (id) => `/accounting/providers/invoices/${id}`,
    cache: vendorInvoiceCache,
    extractDateMs: (invoice) => invoice?.dates?.finalDate?.time ?? null,
    startMs,
    endMs,
    label: `Stroški ${year}`,
    // "Bill Received" in the XTRF UI = BILL_CREATED in the API.
    requireStatus: "BILL_CREATED",
  });
  return { year, amount: combined.amount, count: combined.count, rates: combined.rates };
}

// YTD turnover from client invoices (totalNetto, i.e. excl. VAT), based on
// each invoice's real `dates.invoiceDate` - unlike projects, invoices do
// carry a genuine issue date, so this isn't the same "touched today" proxy
// used elsewhere.
export async function computeYtdTurnover() {
  return computeTurnoverForRange(currentYtdRange());
}

// Sum of client invoices issued this year that are now FULLY paid (payments
// >= totalGross), reported as totalNetto for consistency with
// computeYtdTurnover. Reuses the same clientInvoiceCache (so the
// currencyId/totalNetto/totalGross/dateMs fields are shared, never
// re-fetched twice). Paid-status itself is only cached once TRUE - a fully
// paid invoice stays paid, so it's never re-checked again, but an invoice
// not yet fully paid is re-checked every run (its payments can still
// change) until it is.
export async function computeYtdPaidTurnover() {
  const { year, startMs, endMs } = currentYtdRange();
  const invoiceIds = await xtrfRequest("GET", "/accounting/customers/invoices/ids", { updatedSince: startMs });

  await clientInvoiceCache.load();
  let cacheHits = 0;
  let paymentChecks = 0;

  const totals = {};
  const counts = {};
  for (const id of invoiceIds) {
    let entry = clientInvoiceCache.get(id);
    if (entry && entry.totalGross !== undefined) {
      cacheHits++;
    } else {
      const invoice = await xtrfRequest("GET", `/accounting/customers/invoices/${id}`);
      entry = {
        ...entry,
        currencyId: invoice?.currencyId,
        totalNetto: invoice?.totalNetto,
        totalGross: invoice?.totalGross,
        dateMs: invoice?.dates?.invoiceDate?.time ?? null,
      };
      clientInvoiceCache.set(id, entry);
    }

    const { currencyId, totalNetto, totalGross, dateMs } = entry;
    if (currencyId === undefined || typeof totalNetto !== "number") {
      continue;
    }
    if (typeof dateMs !== "number" || dateMs < startMs || dateMs >= endMs) {
      continue;
    }

    let isFullyPaid = entry.isFullyPaid === true;
    if (!isFullyPaid) {
      const payments = await xtrfRequest("GET", `/accounting/customers/invoices/${id}/payments`);
      paymentChecks++;
      const paidSum = Array.isArray(payments) ? payments.reduce((acc, p) => acc + (p.amount ?? 0), 0) : 0;
      isFullyPaid = typeof totalGross === "number" && paidSum >= totalGross - 0.01;
      if (isFullyPaid) {
        entry.isFullyPaid = true;
        clientInvoiceCache.set(id, entry);
      }
    }

    if (isFullyPaid) {
      addToTotals(totals, currencyId, totalNetto);
      counts[currencyId] = (counts[currencyId] ?? 0) + 1;
    }
  }

  await clientInvoiceCache.saveIfDirty();
  console.log(
    `YTD plačano: ${invoiceIds.length} računov, ${cacheHits} osnovnih podatkov iz cache, ${paymentChecks} preverjenih plačil.`
  );

  const combined = await combineIntoEur(totals, counts);
  return { year, amount: combined.amount, count: combined.count, rates: combined.rates };
}

// YTD costs from vendor (provider) invoices - the accounts-payable
// counterpart to computeYtdTurnover. Vendor invoices have no "invoiceDate"
// field; `dates.finalDate` (when the invoice became final) is the closest
// analog.
export async function computeYtdCosts() {
  return computeCostsForRange(currentYtdRange());
}

// Sum of vendor invoices issued this year with paymentStatus FULLY_PAID.
// Unlike client invoices, vendor invoices carry paymentStatus directly on
// the invoice object (no separate payments-list call needed). Reuses
// vendorInvoiceCache. FULLY_PAID is a final state so it's cached
// permanently once reached; anything else is re-fetched every run since
// its status can still change.
export async function computeYtdPaidCosts() {
  const { year, startMs, endMs } = currentYtdRange();
  const invoiceIds = await xtrfRequest("GET", "/accounting/providers/invoices/ids", { updatedSince: startMs });

  await vendorInvoiceCache.load();
  let cacheHits = 0;
  let fetched = 0;

  const totals = {};
  const counts = {};
  for (const id of invoiceIds) {
    let entry = vendorInvoiceCache.get(id);
    // Require `status` to be cached too (not just paymentStatus) so this
    // doesn't depend on computeYtdCosts() having already populated it in
    // the same run - both read/write this cache concurrently via
    // Promise.all, so each must be self-sufficient to avoid a race where
    // one reads the other's incomplete, not-yet-updated entry.
    if (!entry || entry.paymentStatus !== "FULLY_PAID" || entry.status === undefined) {
      const invoice = await xtrfRequest("GET", `/accounting/providers/invoices/${id}`);
      fetched++;
      entry = {
        ...entry,
        currencyId: invoice?.currencyId,
        totalNetto: invoice?.totalNetto,
        totalGross: invoice?.totalGross,
        dateMs: invoice?.dates?.finalDate?.time ?? null,
        status: invoice?.status,
        paymentStatus: invoice?.paymentStatus,
      };
      vendorInvoiceCache.set(id, entry);
    } else {
      cacheHits++;
    }

    const { currencyId, totalNetto, dateMs, status, paymentStatus } = entry;
    if (currencyId === undefined || typeof totalNetto !== "number") {
      continue;
    }
    // "Bill Received" in the XTRF UI = BILL_CREATED in the API - only count
    // costs that have actually been recorded as a real vendor bill.
    if (status !== "BILL_CREATED") {
      continue;
    }
    if (typeof dateMs !== "number" || dateMs < startMs || dateMs >= endMs) {
      continue;
    }
    if (paymentStatus !== "FULLY_PAID") {
      continue;
    }
    addToTotals(totals, currencyId, totalNetto);
    counts[currencyId] = (counts[currencyId] ?? 0) + 1;
  }

  await vendorInvoiceCache.saveIfDirty();
  console.log(`YTD plačani stroški: ${invoiceIds.length} računov, ${cacheHits} iz cache, ${fetched} preverjenih.`);

  const combined = await combineIntoEur(totals, counts);
  return { year, amount: combined.amount, count: combined.count, rates: combined.rates };
}

// Same period last year (Jan 1 - same calendar day), for YoY comparison.
export async function computePriorYtdTurnover() {
  return computeTurnoverForRange(priorYtdRange());
}

export async function computePriorYtdCosts() {
  return computeCostsForRange(priorYtdRange());
}

// Project-based YTD revenue/cost, split by project status - a different
// view than the invoice-based Izdani/Prejeti računi cards above (those
// reflect what's actually been billed; this reflects the underlying
// project pipeline: work already finished (CLOSED) vs still in flight
// (OPENED)). Candidates are fetched via updatedSince=start-of-year, then
// filtered to actualStartDate (falling back to startDate) within this
// year, matching the same "today/this week" project convention used
// elsewhere. A CLOSED project's financials are treated as final and
// cached permanently; an OPENED project is still moving, so it's always
// refetched fresh.
export async function computeProjectYtdSummary() {
  const { year, startMs, endMs } = currentYtdRange();
  const projectIds = await xtrfRequest("GET", "/projects/ids", { updatedSince: startMs });

  await projectCache.load();
  let cacheHits = 0;

  const revenueClosed = {};
  const revenueClosedCounts = {};
  const revenueOpen = {};
  const revenueOpenCounts = {};
  const costClosed = {};
  const costClosedCounts = {};
  const costOpen = {};
  const costOpenCounts = {};

  for (const id of projectIds) {
    let entry = projectCache.get(id);
    if (!entry || entry.status !== "CLOSED") {
      const project = await xtrfRequest("GET", `/projects/${id}`);
      entry = {
        currencyId: project?.finance?.currencyId,
        totalAgreed: project?.finance?.totalAgreed,
        totalCost: project?.finance?.totalCost,
        status: project?.status,
        startedMs: project?.dates?.actualStartDate?.time ?? project?.dates?.startDate?.time ?? null,
      };
      projectCache.set(id, entry);
    } else {
      cacheHits++;
    }

    const { currencyId, totalAgreed, totalCost, status, startedMs } = entry;
    if (currencyId === undefined) {
      continue;
    }
    if (typeof startedMs !== "number" || startedMs < startMs || startedMs >= endMs) {
      continue;
    }

    if (status === "CLOSED") {
      if (typeof totalAgreed === "number") {
        addToTotals(revenueClosed, currencyId, totalAgreed);
        revenueClosedCounts[currencyId] = (revenueClosedCounts[currencyId] ?? 0) + 1;
      }
      if (typeof totalCost === "number") {
        addToTotals(costClosed, currencyId, totalCost);
        costClosedCounts[currencyId] = (costClosedCounts[currencyId] ?? 0) + 1;
      }
    } else if (status === "OPENED") {
      if (typeof totalAgreed === "number") {
        addToTotals(revenueOpen, currencyId, totalAgreed);
        revenueOpenCounts[currencyId] = (revenueOpenCounts[currencyId] ?? 0) + 1;
      }
      if (typeof totalCost === "number") {
        addToTotals(costOpen, currencyId, totalCost);
        costOpenCounts[currencyId] = (costOpenCounts[currencyId] ?? 0) + 1;
      }
    }
  }

  await projectCache.saveIfDirty();
  console.log(`Projekti ${year}: ${projectIds.length} kandidatov, ${cacheHits} zaprtih iz cache.`);

  const [revClosed, revOpen, cClosed, cOpen] = await Promise.all([
    combineIntoEur(revenueClosed, revenueClosedCounts),
    combineIntoEur(revenueOpen, revenueOpenCounts),
    combineIntoEur(costClosed, costClosedCounts),
    combineIntoEur(costOpen, costOpenCounts),
  ]);

  return {
    year,
    revenueClosed: { amount: revClosed.amount, count: revClosed.count },
    revenueOpen: { amount: revOpen.amount, count: revOpen.count },
    costClosed: { amount: cClosed.amount, count: cClosed.count },
    costOpen: { amount: cOpen.amount, count: cOpen.count },
  };
}

export async function computeAll() {
  const [totalAgreed, week, paid, paidWeek] = await Promise.all([
    computeTotalAgreedToday(),
    computeTotalAgreedThisWeek(),
    computePaidInvoicesToday(),
    computePaidInvoicesThisWeek(),
  ]);
  return {
    totalAgreed,
    totalAgreedWeek: week.totals,
    totalAgreedWeekRates: week.rates,
    paidInvoices: paid.totals,
    paidInvoiceRates: paid.rates,
    paidInvoicesWeek: paidWeek.totals,
    paidInvoicesWeekRates: paidWeek.rates,
    generatedAt: new Date().toISOString(),
  };
}
