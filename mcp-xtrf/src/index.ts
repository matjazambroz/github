#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { XtrfClient, type XtrfMethod } from "./xtrfClient.js";
import { dateOnlyToEpochMs } from "./dateUtils.js";

const client = new XtrfClient();
const instanceTimeZone = process.env.XTRF_TIMEZONE ?? "Europe/Ljubljana";

const server = new McpServer({
  name: "mcp-xtrf",
  version: "0.1.0",
});

function formatResult(result: { status: number; ok: boolean; body: unknown }) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify({ status: result.status, ok: result.ok, body: result.body }, null, 2),
      },
    ],
    isError: !result.ok,
  };
}

server.registerTool(
  "xtrf_request",
  {
    title: "XTRF raw request",
    description:
      "Call an arbitrary XTRF API endpoint (relative to XTRF_BASE_URL + XTRF_API_BASE_PATH). " +
      "Use this for any operation not covered by a dedicated tool, or when the exact endpoint " +
      "path/shape needs to be confirmed against the XTRF API docs for this instance.",
    inputSchema: {
      method: z.enum(["GET", "POST", "PUT", "PATCH", "DELETE"]).describe("HTTP method"),
      path: z.string().describe('API path, e.g. "/projects" or "/projects/123/jobs"'),
      query: z
        .record(z.union([z.string(), z.number(), z.boolean()]))
        .optional()
        .describe("Query string parameters"),
      body: z.unknown().optional().describe("JSON request body, for POST/PUT/PATCH"),
    },
  },
  async ({ method, path, query, body }) => {
    const result = await client.request({ method: method as XtrfMethod, path, query, body });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_project_ids",
  {
    title: "List XTRF project IDs",
    description:
      "List project IDs, optionally only those modified since (midnight of) a given date. " +
      "Wraps GET /projects/ids (confirmed against the live instance). The date is converted " +
      `to the epoch-ms timestamp the API expects, using the ${instanceTimeZone} time zone ` +
      "(override with XTRF_TIMEZONE).",
    inputSchema: {
      updatedSince: z
        .string()
        .date()
        .optional()
        .describe('Only return projects modified since midnight of this date, e.g. "2026-08-24"'),
    },
  },
  async ({ updatedSince }) => {
    const updatedSinceMs = updatedSince ? dateOnlyToEpochMs(updatedSince, instanceTimeZone) : undefined;
    const result = await client.request({
      method: "GET",
      path: "/projects/ids",
      query: { updatedSince: updatedSinceMs },
    });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_get_project",
  {
    title: "Get XTRF project",
    description: "Get a single project by ID. Wraps GET /projects/{projectId}.",
    inputSchema: {
      projectId: z.union([z.string(), z.number()]).describe("Project ID"),
    },
  },
  async ({ projectId }) => {
    const result = await client.request({ method: "GET", path: `/projects/${projectId}` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_search_projects",
  {
    title: "Search XTRF projects by client and/or status",
    description:
      "Finds Classic projects matching a client (customerId) and/or status (e.g. OPENED), " +
      "for questions like 'which open projects do we have for client X' or 'how many projects " +
      "were touched today'. The XTRF API has no direct search-by-client or search-by-status " +
      "endpoint (only /browser, which needs a view pre-saved in the XTRF UI), so this fetches " +
      "candidate project IDs via GET /projects/ids and then GET /projects/{id} for each one, " +
      "filtering client-side. ALWAYS pass updatedSince when you can (e.g. today's date, or the " +
      "start of the relevant period) to keep this fast and bound the candidate set - otherwise " +
      "up to maxCandidates of the most recently created projects are checked and older matches " +
      "may be missed. Note there is no explicit 'created date' field; updatedSince matches on " +
      "last-modified time, which is a reasonable proxy for 'created today' on brand-new projects " +
      "but will also catch projects merely edited today.",
    inputSchema: {
      customerId: z
        .union([z.string(), z.number()])
        .optional()
        .describe("Only match this client/customer ID (find it via xtrf_list_clients or xtrf_get_client)"),
      status: z
        .string()
        .optional()
        .describe('Only match this project status, e.g. "OPENED", "CLOSED", "CANCELLED"'),
      updatedSince: z
        .string()
        .date()
        .optional()
        .describe('Only consider projects modified since midnight of this date, e.g. "2026-08-26"'),
      maxCandidates: z
        .number()
        .int()
        .positive()
        .max(1000)
        .optional()
        .describe("Max number of project IDs to fetch and check, newest first (default 200)"),
    },
  },
  async ({ customerId, status, updatedSince, maxCandidates }) => {
    const updatedSinceMs = updatedSince ? dateOnlyToEpochMs(updatedSince, instanceTimeZone) : undefined;
    const idsResult = await client.request({
      method: "GET",
      path: "/projects/ids",
      query: { updatedSince: updatedSinceMs },
    });

    if (!idsResult.ok) {
      return formatResult(idsResult);
    }

    const allIds = Array.isArray(idsResult.body) ? (idsResult.body as number[]) : [];
    const cap = maxCandidates ?? 200;
    const candidateIds = [...allIds].sort((a, b) => b - a).slice(0, cap);

    const matches: unknown[] = [];
    for (const id of candidateIds) {
      const projectResult = await client.request({ method: "GET", path: `/projects/${id}` });
      if (!projectResult.ok) {
        continue;
      }
      const project = projectResult.body as Record<string, unknown>;
      if (customerId !== undefined && String(project.customerId) !== String(customerId)) {
        continue;
      }
      if (status !== undefined && project.status !== status) {
        continue;
      }
      matches.push(project);
    }

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              totalCandidateIds: allIds.length,
              checkedCandidates: candidateIds.length,
              truncated: allIds.length > candidateIds.length,
              matchCount: matches.length,
              matches,
            },
            null,
            2
          ),
        },
      ],
      isError: false,
    };
  }
);

server.registerTool(
  "xtrf_get_job",
  {
    title: "Get XTRF job",
    description: "Get a single (Classic) job by ID. Wraps GET /jobs/{jobId}.",
    inputSchema: {
      jobId: z.string().describe("Job ID"),
    },
  },
  async ({ jobId }) => {
    const result = await client.request({ method: "GET", path: `/jobs/${jobId}` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_project_jobs",
  {
    title: "List jobs in an XTRF project",
    description:
      "List all jobs belonging to a (Smart) project. Wraps GET /v2/projects/{projectId}/jobs " +
      '(the OpenAPI spec has no generic "list all jobs" endpoint, only this per-project one and ' +
      "GET /jobs/{jobId} for a single Classic job).",
    inputSchema: {
      projectId: z.union([z.string(), z.number()]).describe("Project ID"),
    },
  },
  async ({ projectId }) => {
    const result = await client.request({ method: "GET", path: `/v2/projects/${projectId}/jobs` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_clients",
  {
    title: "List XTRF clients",
    description:
      'List clients (called "customers" in the XTRF Home API). Wraps GET /customers ' +
      '("Returns list of simple clients representations").',
    inputSchema: {
      updatedSince: z
        .string()
        .date()
        .optional()
        .describe('Only return clients modified since midnight of this date, e.g. "2026-08-24"'),
      excludeErased: z.boolean().optional().describe("Filter out erased clients; default: false"),
    },
  },
  async ({ updatedSince, excludeErased }) => {
    const updatedSinceMs = updatedSince ? dateOnlyToEpochMs(updatedSince, instanceTimeZone) : undefined;
    const result = await client.request({
      method: "GET",
      path: "/customers",
      query: { updatedSince: updatedSinceMs, excludeErased },
    });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_get_client",
  {
    title: "Get XTRF client",
    description:
      "Get a single client (\"customer\" in the XTRF Home API) by ID. Wraps GET /customers/{clientId}. " +
      "Project responses reference this ID as customerId.",
    inputSchema: {
      clientId: z.union([z.string(), z.number()]).describe("Client/customer ID"),
    },
  },
  async ({ clientId }) => {
    const result = await client.request({ method: "GET", path: `/customers/${clientId}` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_currencies",
  {
    title: "List XTRF currencies",
    description:
      'Look up currency codes/names by ID (e.g. to resolve a "currencyId" field seen on a ' +
      "project's or client's finance data into a readable ISO code like \"EUR\"). There is no " +
      'dedicated /currencies endpoint - this wraps the generic dictionary endpoint ' +
      "GET /dictionaries/currency/active or GET /dictionaries/currency/all.",
    inputSchema: {
      activeOnly: z
        .boolean()
        .optional()
        .describe("Only return active currencies (default true). Set false to include inactive ones."),
      nameEquals: z.string().optional().describe("Filter to the exact localized name of one currency"),
    },
  },
  async ({ activeOnly, nameEquals }) => {
    const path = activeOnly === false ? "/dictionaries/currency/all" : "/dictionaries/currency/active";
    const result = await client.request({ method: "GET", path, query: { nameEquals } });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_get_currency",
  {
    title: "Get XTRF currency by ID",
    description:
      'Resolve a single currency dictionary ID (as seen in a "currencyId" field) to its details ' +
      "(name, ISO code, symbol). Wraps GET /dictionaries/currency/{id}.",
    inputSchema: {
      currencyId: z.union([z.string(), z.number()]).describe("Currency dictionary ID"),
    },
  },
  async ({ currencyId }) => {
    const result = await client.request({ method: "GET", path: `/dictionaries/currency/${currencyId}` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_invoice_ids",
  {
    title: "List XTRF client invoice IDs",
    description:
      "List client invoice IDs, optionally only those modified since (midnight of) a given date. " +
      "Wraps GET /accounting/customers/invoices/ids. Note updatedSince matches on last-modified " +
      "time (e.g. a new payment recorded against the invoice), not the invoice's original issue date.",
    inputSchema: {
      updatedSince: z
        .string()
        .date()
        .optional()
        .describe('Only return invoices modified since midnight of this date, e.g. "2026-08-24"'),
    },
  },
  async ({ updatedSince }) => {
    const updatedSinceMs = updatedSince ? dateOnlyToEpochMs(updatedSince, instanceTimeZone) : undefined;
    const result = await client.request({
      method: "GET",
      path: "/accounting/customers/invoices/ids",
      query: { updatedSince: updatedSinceMs },
    });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_get_invoice",
  {
    title: "Get XTRF client invoice",
    description:
      "Get a single client invoice by ID, including status, totals, currencyId and dates. " +
      "Wraps GET /accounting/customers/invoices/{invoiceId}.",
    inputSchema: {
      invoiceId: z.union([z.string(), z.number()]).describe("Invoice ID"),
    },
  },
  async ({ invoiceId }) => {
    const result = await client.request({ method: "GET", path: `/accounting/customers/invoices/${invoiceId}` });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_get_invoice_payments",
  {
    title: "List payments on an XTRF client invoice",
    description:
      "List all payments recorded against a client invoice (amount, paymentDate, paymentMethodId). " +
      "Wraps GET /accounting/customers/invoices/{invoiceId}/payments.",
    inputSchema: {
      invoiceId: z.union([z.string(), z.number()]).describe("Invoice ID"),
    },
  },
  async ({ invoiceId }) => {
    const result = await client.request({
      method: "GET",
      path: `/accounting/customers/invoices/${invoiceId}/payments`,
    });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_search_paid_invoices",
  {
    title: "Find invoice payments recorded on a given date",
    description:
      "Finds client-invoice payments whose paymentDate falls on a given day, for questions like " +
      "'what got paid today'. The XTRF API has no direct 'payments by date' endpoint, so this " +
      "fetches candidate invoice IDs modified since that day via GET /accounting/customers/invoices/ids " +
      "(a new payment updates the invoice's modified date), then checks each candidate's " +
      "GET .../payments, filtering client-side to payments actually dated that day, and fetches " +
      "GET .../{invoiceId} (for currencyId and totals) only for candidates with a matching payment. " +
      "ALWAYS pass date as the day you care about. Note an invoice can be modified for reasons " +
      "other than a payment (status change, etc.), so candidates without a matching payment are " +
      "silently skipped - this is expected, not an error.",
    inputSchema: {
      date: z.string().date().describe('The day to check, e.g. "2026-08-27"'),
      maxCandidates: z
        .number()
        .int()
        .positive()
        .max(1000)
        .optional()
        .describe("Max number of invoice IDs to check, newest first (default 200)"),
    },
  },
  async ({ date, maxCandidates }) => {
    const dayStartMs = dateOnlyToEpochMs(date, instanceTimeZone);
    const dayEndMs = dayStartMs + 24 * 60 * 60 * 1000;

    const idsResult = await client.request({
      method: "GET",
      path: "/accounting/customers/invoices/ids",
      query: { updatedSince: dayStartMs },
    });

    if (!idsResult.ok) {
      return formatResult(idsResult);
    }

    const allIds = Array.isArray(idsResult.body) ? (idsResult.body as number[]) : [];
    const cap = maxCandidates ?? 200;
    const candidateIds = [...allIds].sort((a, b) => b - a).slice(0, cap);

    const matches: unknown[] = [];
    for (const id of candidateIds) {
      const paymentsResult = await client.request({
        method: "GET",
        path: `/accounting/customers/invoices/${id}/payments`,
      });
      if (!paymentsResult.ok) {
        continue;
      }

      const payments = Array.isArray(paymentsResult.body)
        ? (paymentsResult.body as Array<Record<string, unknown>>)
        : [];
      const dayPayments = payments.filter((p) => {
        const dateField = p.paymentDate as { time?: number } | undefined;
        const t = dateField?.time;
        return typeof t === "number" && t >= dayStartMs && t < dayEndMs;
      });
      if (dayPayments.length === 0) {
        continue;
      }

      const invoiceResult = await client.request({
        method: "GET",
        path: `/accounting/customers/invoices/${id}`,
      });
      const invoice = invoiceResult.ok ? invoiceResult.body : { id };
      matches.push({ invoice, payments: dayPayments });
    }

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              totalCandidateIds: allIds.length,
              checkedCandidates: candidateIds.length,
              truncated: allIds.length > candidateIds.length,
              matchCount: matches.length,
              matches,
            },
            null,
            2
          ),
        },
      ],
      isError: false,
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
