import type { TaskStatus } from "@/types/task";

export type DueUrgency = "overdue" | "due_soon" | null;

const DUE_SOON_WINDOW_DAYS = 3;

function startOfTodayUTC() {
  const now = new Date();
  return Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
}

export function getDueUrgency(dueDate: string | null, status: TaskStatus): DueUrgency {
  if (!dueDate || status === "done") return null;

  // Date-only strings (e.g. "2026-09-05") parse as UTC midnight, so compare
  // against a UTC "today" rather than the server's local midnight.
  const due = new Date(dueDate).getTime();
  const today = startOfTodayUTC();
  const daysUntilDue = Math.round((due - today) / 86_400_000);

  if (daysUntilDue < 0) return "overdue";
  if (daysUntilDue <= DUE_SOON_WINDOW_DAYS) return "due_soon";
  return null;
}

export function formatDueDate(dueDate: string, options?: { includeYear?: boolean }): string {
  return new Date(dueDate).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: options?.includeYear ? "numeric" : undefined,
    timeZone: "UTC",
  });
}
