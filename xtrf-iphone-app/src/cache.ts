import { xtrfRequest, type XtrfEnv } from "./xtrfClient";

// Currency id -> ISO code never changes, so it's cached in KV forever.
export async function resolveCurrency(env: XtrfEnv & { CACHE: KVNamespace }, currencyId: number): Promise<string> {
  const key = `currency:${currencyId}`;
  const cached = await env.CACHE.get(key);
  if (cached) {
    return cached;
  }
  const currency = await xtrfRequest<{ isoCode?: string }>(env, "GET", `/dictionaries/currency/${currencyId}`);
  const isoCode = currency?.isoCode ?? `#${currencyId}`;
  await env.CACHE.put(key, isoCode);
  return isoCode;
}

// XTRF's base/default currency is EUR. GET /dictionaries/currency/{isoCode}/exchangeRate
// returns how many units of that currency equal 1 EUR, sourced from
// OpenExchangeRates.org and refreshed daily by XTRF - cached in KV for a few
// hours only (not forever, unlike currency ids).
export async function resolveEurExchangeRate(
  env: XtrfEnv & { CACHE: KVNamespace },
  isoCode: string
): Promise<{ rate: number; date: string | null }> {
  if (isoCode === "EUR") {
    return { rate: 1, date: null };
  }
  const key = `rate:${isoCode}`;
  const cached = await env.CACHE.get(key, "json");
  if (cached) {
    return cached as { rate: number; date: string | null };
  }
  const data = await xtrfRequest<{ exchangeRate?: string; publicationDate?: { time: number }; dateFrom?: { time: number } }>(
    env,
    "GET",
    `/dictionaries/currency/${isoCode}/exchangeRate`
  );
  const rate = parseFloat(data?.exchangeRate ?? "");
  const dateMs = data?.publicationDate?.time ?? data?.dateFrom?.time;
  const result = { rate, date: dateMs ? new Date(dateMs).toISOString() : null };
  await env.CACHE.put(key, JSON.stringify(result), { expirationTtl: 6 * 60 * 60 });
  return result;
}

export interface CombinedEur {
  amount: number;
  count: number;
}

// Combines per-currency totals (keyed by currencyId) into a single EUR
// amount using XTRF's own exchange rates.
export async function combineIntoEur(
  env: XtrfEnv & { CACHE: KVNamespace },
  totalsByCurrencyId: Record<string, number>,
  counts: Record<string, number>
): Promise<CombinedEur> {
  let amount = 0;
  let count = 0;
  for (const [currencyId, total] of Object.entries(totalsByCurrencyId)) {
    const code = await resolveCurrency(env, Number(currencyId));
    const { rate } = await resolveEurExchangeRate(env, code);
    amount += rate ? total / rate : total;
    count += counts[currencyId] ?? 0;
  }
  return { amount, count };
}

export interface InvoiceCacheEntry {
  currencyId?: number;
  totalNetto?: number;
  dateMs?: number | null;
  status?: string;
}

export async function getCachedInvoice(env: { CACHE: KVNamespace }, id: number): Promise<InvoiceCacheEntry | null> {
  return (await env.CACHE.get(`invoice:${id}`, "json")) as InvoiceCacheEntry | null;
}

export async function putCachedInvoice(env: { CACHE: KVNamespace }, id: number, entry: InvoiceCacheEntry): Promise<void> {
  // Once a client invoice is issued, its currencyId/totalNetto/date/status
  // don't meaningfully change again, so this is cached indefinitely (no TTL).
  await env.CACHE.put(`invoice:${id}`, JSON.stringify(entry));
}
