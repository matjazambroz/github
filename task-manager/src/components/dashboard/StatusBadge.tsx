import type { ProjectStatus } from "@/types/project";

const STATUS_STYLES: Record<ProjectStatus, string> = {
  not_started: "bg-gray-100 text-gray-700 dark:bg-gray-500/20 dark:text-gray-300",
  in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
  on_hold: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300",
};

const STATUS_LABELS: Record<ProjectStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  on_hold: "On hold",
  completed: "Completed",
};

export function StatusBadge({ status }: { status: ProjectStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
