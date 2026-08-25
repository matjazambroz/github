#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { XtrfClient, type XtrfMethod } from "./xtrfClient.js";

const client = new XtrfClient();

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
  "xtrf_list_projects",
  {
    title: "List XTRF projects",
    description: "List projects, with optional filtering/pagination. Wraps GET /projects.",
    inputSchema: {
      status: z.string().optional().describe("Filter by project status, if supported"),
      client: z.string().optional().describe("Filter by client ID, if supported"),
      limit: z.number().int().positive().max(500).optional(),
      offset: z.number().int().nonnegative().optional(),
    },
  },
  async ({ status, client: clientId, limit, offset }) => {
    const result = await client.request({
      method: "GET",
      path: "/projects",
      query: { status, client: clientId, limit, offset },
    });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_project_ids",
  {
    title: "List XTRF project IDs",
    description:
      "List project IDs, optionally only those modified since a given timestamp. " +
      "Wraps GET /projects/ids (confirmed against the live instance).",
    inputSchema: {
      updatedSince: z
        .number()
        .int()
        .optional()
        .describe("Unix epoch milliseconds ($int64) - only return projects modified since this time"),
    },
  },
  async ({ updatedSince }) => {
    const result = await client.request({
      method: "GET",
      path: "/projects/ids",
      query: { updatedSince },
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
  "xtrf_list_jobs",
  {
    title: "List XTRF jobs",
    description:
      "List jobs, optionally scoped to a project. Wraps GET /jobs or GET /projects/{projectId}/jobs.",
    inputSchema: {
      projectId: z.union([z.string(), z.number()]).optional(),
      status: z.string().optional().describe("Filter by job status, if supported"),
      limit: z.number().int().positive().max(500).optional(),
      offset: z.number().int().nonnegative().optional(),
    },
  },
  async ({ projectId, status, limit, offset }) => {
    const path = projectId ? `/projects/${projectId}/jobs` : "/jobs";
    const result = await client.request({ method: "GET", path, query: { status, limit, offset } });
    return formatResult(result);
  }
);

server.registerTool(
  "xtrf_list_clients",
  {
    title: "List XTRF clients",
    description:
      "List clients (called \"customers\" in the XTRF Home API), with optional pagination. " +
      "Wraps GET /customers.",
    inputSchema: {
      limit: z.number().int().positive().max(500).optional(),
      offset: z.number().int().nonnegative().optional(),
    },
  },
  async ({ limit, offset }) => {
    const result = await client.request({ method: "GET", path: "/customers", query: { limit, offset } });
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

const transport = new StdioServerTransport();
await server.connect(transport);
