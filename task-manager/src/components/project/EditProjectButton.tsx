"use client";

import { useState, useTransition } from "react";
import { updateProject } from "@/app/actions/projects";
import type { Project } from "@/types/project";

export function EditProjectButton({ project }: { project: Project }) {
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function close() {
    setIsOpen(false);
    setError(null);
  }

  function handleSubmit(formData: FormData) {
    startTransition(async () => {
      const result = await updateProject(project.id, formData);
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
        className="rounded-lg border border-black/15 px-4 py-2 text-sm font-medium hover:bg-black/5 dark:border-white/15 dark:hover:bg-white/10"
      >
        Edit
      </button>

      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={close}
        >
          <div
            className="w-full max-w-md rounded-xl bg-white p-6 dark:bg-neutral-900"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-semibold">Edit project</h2>

            <form action={handleSubmit} className="mt-4 flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label htmlFor="edit-project-name" className="text-sm font-medium">
                  Name
                </label>
                <input
                  id="edit-project-name"
                  name="name"
                  required
                  defaultValue={project.name}
                  className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label htmlFor="edit-project-description" className="text-sm font-medium">
                  Description
                </label>
                <textarea
                  id="edit-project-description"
                  name="description"
                  rows={3}
                  defaultValue={project.description ?? ""}
                  className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1">
                  <label htmlFor="edit-project-status" className="text-sm font-medium">
                    Status
                  </label>
                  <select
                    id="edit-project-status"
                    name="status"
                    defaultValue={project.status}
                    className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
                  >
                    <option value="not_started">Not started</option>
                    <option value="in_progress">In progress</option>
                    <option value="on_hold">On hold</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label htmlFor="edit-project-due_date" className="text-sm font-medium">
                    Due date
                  </label>
                  <input
                    id="edit-project-due_date"
                    name="due_date"
                    type="date"
                    defaultValue={project.due_date ?? ""}
                    className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
                  />
                </div>
              </div>

              {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

              <div className="mt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={close}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-black/60 hover:text-black dark:text-white/60 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isPending}
                  className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 dark:bg-white dark:text-black"
                >
                  {isPending ? "Saving…" : "Save changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
