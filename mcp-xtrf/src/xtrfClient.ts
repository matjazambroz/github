type XtrfAuthMode = "apikey" | "oauth2" | "classic_login";

interface XtrfConfig {
  baseUrl: string;
  basePath: string;
  authMode: XtrfAuthMode;
  // XTRF Home API uses a versioned media type, e.g.
  // "application/vnd.xtrf-v1+json;charset=UTF-8", instead of application/json.
  acceptHeader: string;
  // apikey mode
  apiKey?: string;
  apiKeyHeader: string;
  apiKeyPrefix: string;
  // oauth2 mode
  clientId?: string;
  clientSecret?: string;
  tokenUrl?: string;
  // classic_login mode (XTRF Classic REST API v2 session login)
  loginUrl?: string;
  username?: string;
  password?: string;
  sessionHeader: string;
  sessionTokenField: string;
}

const AUTH_MODES: XtrfAuthMode[] = ["apikey", "oauth2", "classic_login"];

function loadConfig(): XtrfConfig {
  const baseUrl = process.env.XTRF_BASE_URL;
  if (!baseUrl) {
    throw new Error("XTRF_BASE_URL is not set");
  }

  const authMode = (process.env.XTRF_AUTH_MODE ?? "apikey") as XtrfAuthMode;
  if (!AUTH_MODES.includes(authMode)) {
    throw new Error(`Invalid XTRF_AUTH_MODE "${authMode}", expected one of: ${AUTH_MODES.join(", ")}`);
  }

  const basePath = (process.env.XTRF_API_BASE_PATH ?? "/home-api").replace(/\/+$/, "");
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, "");

  return {
    baseUrl: normalizedBaseUrl,
    basePath,
    authMode,
    acceptHeader: process.env.XTRF_ACCEPT_HEADER ?? "application/vnd.xtrf-v1+json;charset=UTF-8",
    apiKey: process.env.XTRF_API_KEY,
    apiKeyHeader: process.env.XTRF_API_KEY_HEADER ?? "X-AUTH-ACCESS-TOKEN",
    apiKeyPrefix: process.env.XTRF_API_KEY_PREFIX ?? "",
    clientId: process.env.XTRF_CLIENT_ID,
    clientSecret: process.env.XTRF_CLIENT_SECRET,
    tokenUrl: process.env.XTRF_TOKEN_URL,
    loginUrl: process.env.XTRF_LOGIN_URL ?? `${normalizedBaseUrl}${basePath}/session`,
    username: process.env.XTRF_USERNAME,
    password: process.env.XTRF_PASSWORD,
    sessionHeader: process.env.XTRF_SESSION_HEADER ?? "X-AUTH-ACCESS-TOKEN",
    sessionTokenField: process.env.XTRF_SESSION_TOKEN_FIELD ?? "id",
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
      return { [this.config.apiKeyHeader]: `${this.config.apiKeyPrefix}${this.config.apiKey}` };
    }

    if (this.config.authMode === "classic_login") {
      const token = await this.getClassicSessionToken();
      return { [this.config.sessionHeader]: token };
    }

    const token = await this.getOAuthToken();
    return { Authorization: `Bearer ${token}` };
  }

  private async getClassicSessionToken(): Promise<string> {
    const now = Date.now();
    if (this.cachedToken && this.cachedToken.expiresAt > now + 5000) {
      return this.cachedToken.value;
    }

    const { loginUrl, username, password, sessionHeader, sessionTokenField } = this.config;
    if (!loginUrl || !username || !password) {
      throw new Error(
        "XTRF_LOGIN_URL, XTRF_USERNAME and XTRF_PASSWORD must all be set (required for authMode=classic_login)"
      );
    }

    const response = await fetch(loginUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(`XTRF Classic session login failed: ${response.status} ${text}`);
    }

    // XTRF Classic returns the session token either as a response header
    // (commonly the same header used on subsequent requests) or in the
    // JSON body under sessionTokenField (default "id"). Try the header first.
    const headerToken = response.headers.get(sessionHeader);
    let token = headerToken ?? undefined;

    if (!token) {
      const json = (await response.json().catch(() => null)) as Record<string, unknown> | null;
      const value = json?.[sessionTokenField];
      if (typeof value === "string") {
        token = value;
      }
    }

    if (!token) {
      throw new Error(
        `Could not extract session token from XTRF Classic login response ` +
          `(checked header "${sessionHeader}" and body field "${sessionTokenField}"). ` +
          `Set XTRF_SESSION_HEADER / XTRF_SESSION_TOKEN_FIELD to match your instance's response shape.`
      );
    }

    // XTRF Classic sessions commonly last around 30 minutes; refresh a bit early.
    this.cachedToken = { value: token, expiresAt: now + 25 * 60 * 1000 };
    return token;
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
      Accept: this.config.acceptHeader,
      ...authHeaders,
    };

    let body: string | undefined;
    if (options.body !== undefined) {
      headers["Content-Type"] = this.config.acceptHeader;
      body = JSON.stringify(options.body);
    }

    const response = await fetch(url, { method: options.method, headers, body });

    const responseHeaders: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    const contentType = response.headers.get("content-type") ?? "";
    let responseBody: unknown;
    if (contentType.includes("json")) {
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
