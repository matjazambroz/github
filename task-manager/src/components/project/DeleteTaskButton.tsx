"use client";

import { useTransition } from "react";
import { deleteTask } from "@/app/actions/tasks";

export function DeleteTaskButton({
  taskId,
  projectId,
  taskTitle,
}: {
  taskId: string;
  projectId: string;
  taskTitle: string;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() => {
        if (!window.confirm(`Delete "${taskTitle}"? This can't be undone.`)) return;
        startTransition(async () => {
          const result = await deleteTask(taskId, projectId);
          if (result?.error) {
            window.alert(result.error);
          }
        });
      }}
      className="text-xs font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
    >
      Delete
    </button>
  );
}
