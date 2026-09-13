export interface XtrfEnv {
  XTRF_BASE_URL: string;
  XTRF_API_BASE_PATH: string;
  XTRF_ACCEPT_HEADER: string;
  XTRF_API_KEY: string;
}

export class XtrfError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

function buildUrl(env: XtrfEnv, path: string, query?: Record<string, string | number | undefined>): string {
  const baseUrl = env.XTRF_BASE_URL.replace(/\/+$/, "");
  const basePath = env.XTRF_API_BASE_PATH.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${baseUrl}${basePath}${normalizedPath}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

export async function xtrfRequest<T>(
  env: XtrfEnv,
  method: string,
  path: string,
  query?: Record<string, string | number | undefined>
): Promise<T> {
  const url = buildUrl(env, path, query);
  const response = await fetch(url, {
    method,
    headers: {
      Accept: env.XTRF_ACCEPT_HEADER,
      "X-AUTH-ACCESS-TOKEN": env.XTRF_API_KEY,
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("json") ? await response.json().catch(() => null) : await response.text();

  if (!response.ok) {
    throw new XtrfError(`XTRF request failed: ${method} ${path} -> ${response.status}`, response.status, body);
  }

  return body as T;
}
