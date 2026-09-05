import type { TaskStatus } from "@/types/task";

export type DueUrgency = "overdue" | "due_soon" | null;

const DUE_SOON_WINDOW_DAYS = 3;

function startOfToday() {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return now;
}

export function getDueUrgency(dueDate: string | null, status: TaskStatus): DueUrgency {
  if (!dueDate || status === "done") return null;

  const due = new Date(dueDate);
  const today = startOfToday();
  const daysUntilDue = Math.round((due.getTime() - today.getTime()) / 86_400_000);

  if (daysUntilDue < 0) return "overdue";
  if (daysUntilDue <= DUE_SOON_WINDOW_DAYS) return "due_soon";
  return null;
}
