"use client";

import { useTransition } from "react";
import { deleteProject } from "@/app/actions/projects";

export function DeleteProjectButton({
  projectId,
  projectName,
}: {
  projectId: string;
  projectName: string;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() => {
        if (
          !window.confirm(
            `Delete "${projectName}"? This also deletes all of its tasks and can't be undone.`,
          )
        )
          return;
        startTransition(() => {
          deleteProject(projectId);
        });
      }}
      className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 dark:border-red-500/30 dark:text-red-400 dark:hover:bg-red-500/10"
    >
      {isPending ? "Deleting…" : "Delete"}
    </button>
  );
}
