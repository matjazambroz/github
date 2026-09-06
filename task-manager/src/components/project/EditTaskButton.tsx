"use client";

import { useState, useTransition } from "react";
import { updateTask } from "@/app/actions/tasks";
import { Modal } from "@/components/ui/Modal";
import type { Task } from "@/types/task";

export function EditTaskButton({ task, projectId }: { task: Task; projectId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function close() {
    setIsOpen(false);
    setError(null);
  }

  function handleSubmit(formData: FormData) {
    startTransition(async () => {
      const result = await updateTask(task.id, projectId, formData);
      if (result.error) {
        setError(result.error);
        return;
      }
      close();
    });
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="text-xs font-medium text-slate-500 hover:text-slate-900"
      >
        Edit
      </button>

      <Modal open={isOpen} onClose={close} title="Edit task">
        <form action={handleSubmit} className="mt-4 flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="edit-title" className="text-sm font-medium">
              Title
            </label>
            <input
              id="edit-title"
              name="title"
              required
              defaultValue={task.title}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="edit-description" className="text-sm font-medium">
              Description
            </label>
            <textarea
              id="edit-description"
              name="description"
              rows={3}
              defaultValue={task.description ?? ""}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="edit-due_date" className="text-sm font-medium">
              Due date
            </label>
            <input
              id="edit-due_date"
              name="due_date"
              type="date"
              defaultValue={task.due_date ?? ""}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={close}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-900"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded-lg bg-blue-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:opacity-50"
            >
              {isPending ? "Saving…" : "Save changes"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
