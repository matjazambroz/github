"use client";

import { useRef, useState, useTransition } from "react";
import { createTask } from "@/app/actions/tasks";
import { Modal } from "@/components/ui/Modal";
import type { Profile } from "@/types/profile";

export function NewTaskButton({
  projectId,
  members,
}: {
  projectId: string;
  members: Profile[];
}) {
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
      const result = await createTask(projectId, formData);
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
        className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 dark:bg-white dark:text-black"
      >
        New task
      </button>

      <Modal open={isOpen} onClose={close} title="New task">
        <form ref={formRef} action={handleSubmit} className="mt-4 flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="title" className="text-sm font-medium">
              Title
            </label>
            <input
              id="title"
              name="title"
              required
              className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
              placeholder="Write the launch announcement"
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
              className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
              placeholder="Any extra detail for this task"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label htmlFor="due_date" className="text-sm font-medium">
                Due date
              </label>
              <input
                id="due_date"
                name="due_date"
                type="date"
                className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="assignee_id" className="text-sm font-medium">
                Assignee
              </label>
              <select
                id="assignee_id"
                name="assignee_id"
                defaultValue=""
                className="rounded-lg border border-black/15 px-3 py-2 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-transparent dark:focus:border-white/40"
              >
                <option value="">Unassigned</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.email}
                  </option>
                ))}
              </select>
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
              {isPending ? "Creating…" : "Create task"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
