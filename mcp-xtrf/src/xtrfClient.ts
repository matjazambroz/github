interface XtrfConfig {
  baseUrl: string;
  basePath: string;
  authMode: "apikey" | "oauth2";
  apiKey?: string;
  apiKeyHeader: string;
  clientId?: string;
  clientSecret?: string;
  tokenUrl?: string;
}

function loadConfig(): XtrfConfig {
  const baseUrl = process.env.XTRF_BASE_URL;
  if (!baseUrl) {
    throw new Error("XTRF_BASE_URL is not set");
  }

  const authMode = (process.env.XTRF_AUTH_MODE ?? "apikey") as "apikey" | "oauth2";
  if (authMode !== "apikey" && authMode !== "oauth2") {
    throw new Error(`Invalid XTRF_AUTH_MODE "${authMode}", expected "apikey" or "oauth2"`);
  }

  return {
    baseUrl: baseUrl.replace(/\/+$/, ""),
    basePath: (process.env.XTRF_API_BASE_PATH ?? "").replace(/\/+$/, ""),
    authMode,
    apiKey: process.env.XTRF_API_KEY,
    apiKeyHeader: process.env.XTRF_API_KEY_HEADER ?? "X-API-KEY",
    clientId: process.env.XTRF_CLIENT_ID,
    clientSecret: process.env.XTRF_CLIENT_SECRET,
    tokenUrl: process.env.XTRF_TOKEN_URL,
  };
}

export type XtrfMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface XtrfRequestOptions {
  method: XtrfMethod;
  path: string;
  query?: Record<string, string | number | boolean | undefined>;
  body?: unknown;
}

export interface XtrfResponse {
  status: number;
  ok: boolean;
  headers: Record<string, string>;
  body: unknown;
}

export class XtrfClient {
  private config: XtrfConfig;
  private cachedToken: { value: string; expiresAt: number } | null = null;

  constructor(config: XtrfConfig = loadConfig()) {
    this.config = config;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    if (this.config.authMode === "apikey") {
      if (!this.config.apiKey) {
        throw new Error("XTRF_API_KEY is not set (required for authMode=apikey)");
      }
      return { [this.config.apiKeyHeader]: this.config.apiKey };
    }

    const token = await this.getOAuthToken();
    return { Authorization: `Bearer ${token}` };
  }

  private async getOAuthToken(): Promise<string> {
    const now = Date.now();
    if (this.cachedToken && this.cachedToken.expiresAt > now + 5000) {
      return this.cachedToken.value;
    }

    const { clientId, clientSecret, tokenUrl } = this.config;
    if (!clientId || !clientSecret || !tokenUrl) {
      throw new Error(
        "XTRF_CLIENT_ID, XTRF_CLIENT_SECRET and XTRF_TOKEN_URL must all be set (required for authMode=oauth2)"
      );
    }

    const response = await fetch(tokenUrl, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: clientId,
        client_secret: clientSecret,
      }),
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(`XTRF OAuth token request failed: ${response.status} ${text}`);
    }

    const json = (await response.json()) as { access_token: string; expires_in?: number };
    const expiresInMs = (json.expires_in ?? 300) * 1000;
    this.cachedToken = { value: json.access_token, expiresAt: now + expiresInMs };
    return json.access_token;
  }

  private buildUrl(path: string, query?: XtrfRequestOptions["query"]): string {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    const url = new URL(`${this.config.baseUrl}${this.config.basePath}${normalizedPath}`);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value !== undefined) {
          url.searchParams.set(key, String(value));
        }
      }
    }
    return url.toString();
  }

  async request(options: XtrfRequestOptions): Promise<XtrfResponse> {
    const authHeaders = await this.getAuthHeaders();
    const url = this.buildUrl(options.path, options.query);

    const headers: Record<string, string> = {
      Accept: "application/json",
      ...authHeaders,
    };

    let body: string | undefined;
    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(options.body);
    }

    const response = await fetch(url, { method: options.method, headers, body });

    const responseHeaders: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    const contentType = response.headers.get("content-type") ?? "";
    let responseBody: unknown;
    if (contentType.includes("application/json")) {
      responseBody = await response.json().catch(() => null);
    } else {
      responseBody = await response.text().catch(() => "");
    }

    return {
      status: response.status,
      ok: response.ok,
      headers: responseHeaders,
      body: responseBody,
    };
  }
}
