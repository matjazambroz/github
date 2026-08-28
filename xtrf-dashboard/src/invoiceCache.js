import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.join(__dirname, "..", "data");

// Once a client/vendor invoice is issued, its currencyId/totalNetto/date
// don't change (payments and status updates don't touch them), so cached
// entries are kept indefinitely - no expiry, no re-fetch. Each call creates
// an independent cache backed by its own file, so client and vendor
// invoices (separate id spaces) never collide.
export function createInvoiceCache(fileName) {
  const cachePath = path.join(dataDir, fileName);
  let cache = null;
  let dirty = false;

  return {
    async load() {
      if (cache) {
        return cache;
      }
      try {
        const raw = await fs.readFile(cachePath, "utf-8");
        cache = JSON.parse(raw);
      } catch {
        cache = {};
      }
      return cache;
    },
    get(id) {
      return cache?.[id];
    },
    set(id, entry) {
      cache[id] = entry;
      dirty = true;
    },
    async saveIfDirty() {
      if (!dirty) {
        return;
      }
      await fs.mkdir(dataDir, { recursive: true });
      await fs.writeFile(cachePath, JSON.stringify(cache));
      dirty = false;
    },
  };
}
