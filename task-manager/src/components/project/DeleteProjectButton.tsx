"use client";

import { useState, useTransition } from "react";
import { deleteProject } from "@/app/actions/projects";

export function DeleteProjectButton({
  projectId,
  projectName,
}: {
  projectId: string;
  projectName: string;
}) {
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <div className="flex flex-col items-end gap-1">
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
          setError(null);
          startTransition(async () => {
            const result = await deleteProject(projectId);
            if (result?.error) {
              setError(result.error);
            }
          });
        }}
        className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
      >
        {isPending ? "Deleting…" : "Delete"}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
