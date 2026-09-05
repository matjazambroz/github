"use client";

import { useRef, useState, useTransition } from "react";
import { createProject } from "@/app/actions/projects";
import { Modal } from "@/components/ui/Modal";

export function NewProjectButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const formRef = useRef<HTMLFormElement>(null);

  function close() {
    setIsOpen(false);
    setError(null);
    formRef.current?.reset();
  }

  function handleSubmit(formData: FormData) {
    startTransition(async () => {
      const result = await createProject(formData);
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
        className="rounded-lg bg-blue-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800"
      >
        New project
      </button>

      <Modal open={isOpen} onClose={close} title="New project">
        <form ref={formRef} action={handleSubmit} className="mt-4 flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="name" className="text-sm font-medium">
              Name
            </label>
            <input
              id="name"
              name="name"
              required
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
              placeholder="Website redesign"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="description" className="text-sm font-medium">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              rows={3}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
              placeholder="What is this project about?"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label htmlFor="status" className="text-sm font-medium">
                Status
              </label>
              <select
                id="status"
                name="status"
                defaultValue="not_started"
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
              >
                <option value="not_started">Not started</option>
                <option value="in_progress">In progress</option>
                <option value="on_hold">On hold</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="due_date" className="text-sm font-medium">
                Due date
              </label>
              <input
                id="due_date"
                name="due_date"
                type="date"
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
              {isPending ? "Creating…" : "Create project"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
