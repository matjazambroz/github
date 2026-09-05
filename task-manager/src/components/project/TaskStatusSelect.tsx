"use client";

import { useTransition } from "react";
import { updateTaskStatus } from "@/app/actions/tasks";
import type { TaskStatus } from "@/types/task";

const STATUS_OPTIONS: { value: TaskStatus; label: string }[] = [
  { value: "todo", label: "To do" },
  { value: "in_progress", label: "In progress" },
  { value: "done", label: "Done" },
];

export function TaskStatusSelect({
  taskId,
  projectId,
  status,
}: {
  taskId: string;
  projectId: string;
  status: TaskStatus;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <select
      value={status}
      disabled={isPending}
      onChange={(e) => {
        const next = e.target.value as TaskStatus;
        startTransition(async () => {
          const result = await updateTaskStatus(taskId, projectId, next);
          if (result?.error) {
            window.alert(result.error);
          }
        });
      }}
      className="rounded-lg border border-black/15 bg-white px-2 py-1 text-xs font-medium outline-none focus:border-black/40 disabled:opacity-50 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
    >
      {STATUS_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
