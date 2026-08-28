const baseUrl = (process.env.XTRF_BASE_URL ?? "").replace(/\/+$/, "");
const basePath = (process.env.XTRF_API_BASE_PATH ?? "/home-api").replace(/\/+$/, "");
const apiKey = process.env.XTRF_API_KEY;
const acceptHeader = process.env.XTRF_ACCEPT_HEADER ?? "application/vnd.xtrf-v1+json;charset=UTF-8";

if (!baseUrl) {
  throw new Error("XTRF_BASE_URL is not set");
}
if (!apiKey) {
  throw new Error("XTRF_API_KEY is not set");
}

function buildUrl(path, query) {
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

export async function xtrfRequest(method, path, query) {
  const url = buildUrl(path, query);
  const response = await fetch(url, {
    method,
    headers: {
      Accept: acceptHeader,
      "X-AUTH-ACCESS-TOKEN": apiKey,
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("json") ? await response.json().catch(() => null) : await response.text();

  if (!response.ok) {
    const error = new Error(`XTRF request failed: ${method} ${path} -> ${response.status}`);
    error.status = response.status;
    error.body = body;
    throw error;
  }

  return body;
}
