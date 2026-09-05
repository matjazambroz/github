"use client";

import { useState, useTransition } from "react";
import { updateProject } from "@/app/actions/projects";
import { Modal } from "@/components/ui/Modal";
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
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
      >
        Edit
      </button>

      <Modal open={isOpen} onClose={close} title="Edit project">
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
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
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
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
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
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
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
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
              />
            </div>
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
