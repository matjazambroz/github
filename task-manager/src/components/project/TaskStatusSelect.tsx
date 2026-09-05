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
      className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-medium outline-none focus:border-blue-900 disabled:opacity-50"
    >
      {STATUS_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
