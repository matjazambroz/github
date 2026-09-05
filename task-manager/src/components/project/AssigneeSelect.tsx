"use client";

import { useTransition } from "react";
import { updateTaskAssignee } from "@/app/actions/tasks";
import type { Profile } from "@/types/profile";

export function AssigneeSelect({
  taskId,
  projectId,
  assigneeId,
  members,
}: {
  taskId: string;
  projectId: string;
  assigneeId: string | null;
  members: Profile[];
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <select
      value={assigneeId ?? ""}
      disabled={isPending}
      onChange={(e) => {
        const next = e.target.value || null;
        startTransition(async () => {
          const result = await updateTaskAssignee(taskId, projectId, next);
          if (result?.error) {
            window.alert(result.error);
          }
        });
      }}
      className="rounded-lg border border-black/15 bg-white px-2 py-1 text-xs font-medium outline-none focus:border-black/40 disabled:opacity-50 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
    >
      <option value="">Unassigned</option>
      {members.map((member) => (
        <option key={member.id} value={member.id}>
          {member.email}
        </option>
      ))}
    </select>
  );
}
