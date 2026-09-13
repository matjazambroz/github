import { computeAll, type AllMetrics } from "./metrics";

// XTRF_API_KEY is a secret (wrangler secret put), so it isn't in
// wrangler.jsonc vars and isn't part of the generated Env - add it here.
declare global {
  interface Env {
    XTRF_API_KEY: string;
  }
}

const LATEST_KEY = "latest";

interface StatusPayload {
  status: "ok" | "error" | "loading";
  data: AllMetrics | null;
  error: string | null;
  updatedAt: string | null;
}

function errorMessage(err: unknown): string {
  const status = (err as { status?: number })?.status;
  if (status === 401) {
    return "XTRF API ključ je neveljaven ali potekel.";
  }
  return err instanceof Error ? err.message : String(err);
}

async function refresh(env: Env): Promise<StatusPayload> {
  const maxInvoicesPerRun = Number(env.MAX_INVOICES_PER_RUN) || 30;
  try {
    const data = await computeAll(env, maxInvoicesPerRun);
    const payload: StatusPayload = { status: "ok", data, error: null, updatedAt: data.generatedAt };
    await env.CACHE.put(LATEST_KEY, JSON.stringify(payload));
    return payload;
  } catch (err) {
    const existing = (await env.CACHE.get(LATEST_KEY, "json")) as StatusPayload | null;
    const payload: StatusPayload = {
      status: "error",
      data: existing?.data ?? null,
      error: errorMessage(err),
      updatedAt: existing?.updatedAt ?? null,
    };
    await env.CACHE.put(LATEST_KEY, JSON.stringify(payload));
    console.error("XTRF refresh failed:", payload.error);
    return payload;
  }
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/data") {
      let payload = (await env.CACHE.get(LATEST_KEY, "json")) as StatusPayload | null;
      if (!payload) {
        // First request ever (nothing cached yet, e.g. right after deploy) -
        // compute once inline so the app isn't stuck waiting for the next
        // cron tick; every later request just reads the cache.
        payload = await refresh(env);
      }
      return Response.json(payload, { headers: { "Cache-Control": "no-store" } });
    }

    return env.ASSETS.fetch(request);
  },

  async scheduled(_event: ScheduledController, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(refresh(env).then(() => undefined));
  },
} satisfies ExportedHandler<Env>;
