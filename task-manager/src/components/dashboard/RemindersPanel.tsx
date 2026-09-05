import Link from "next/link";
import { formatDueDate, getDueUrgency } from "@/lib/due-date";
import type { Task } from "@/types/task";

export interface ReminderTask extends Omit<Task, "due_date"> {
  due_date: string;
  project_name: string;
}

const URGENCY_STYLES = {
  overdue: "border-red-300 bg-red-50 dark:border-red-500/30 dark:bg-red-500/10",
  due_soon: "border-amber-300 bg-amber-50 dark:border-amber-500/30 dark:bg-amber-500/10",
};

const URGENCY_TEXT_STYLES = {
  overdue: "text-red-700 dark:text-red-300",
  due_soon: "text-amber-700 dark:text-amber-300",
};

const URGENCY_LABELS = {
  overdue: "Overdue",
  due_soon: "Due soon",
};

export function RemindersPanel({ tasks }: { tasks: ReminderTask[] }) {
  if (tasks.length === 0) return null;

  return (
    <div className="mb-6 flex flex-col gap-2">
      <h2 className="text-sm font-medium text-black/60 dark:text-white/60">
        Due date reminders
      </h2>
      <div className="flex flex-col gap-2">
        {tasks.map((task) => {
          const urgency = getDueUrgency(task.due_date, task.status) ?? "due_soon";
          return (
            <Link
              key={task.id}
              href={`/projects/${task.project_id}`}
              className={`flex items-center justify-between gap-4 rounded-lg border px-4 py-2.5 text-sm transition-shadow hover:shadow-sm ${URGENCY_STYLES[urgency]}`}
            >
              <div className="min-w-0">
                <span className="font-medium">{task.title}</span>
                <span className="text-black/50 dark:text-white/50"> · {task.project_name}</span>
              </div>
              <span className={`shrink-0 text-xs font-medium ${URGENCY_TEXT_STYLES[urgency]}`}>
                {URGENCY_LABELS[urgency]} · {formatDueDate(task.due_date)}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
