"use client";

import { useRef, useState, useTransition } from "react";
import { inviteMember } from "@/app/actions/members";
import { Modal } from "@/components/ui/Modal";

export function InviteMemberButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isPending, startTransition] = useTransition();
  const formRef = useRef<HTMLFormElement>(null);

  function close() {
    setIsOpen(false);
    setError(null);
    setSuccess(false);
    formRef.current?.reset();
  }

  function handleSubmit(formData: FormData) {
    setSuccess(false);
    startTransition(async () => {
      const result = await inviteMember(formData);
      if (result.error) {
        setError(result.error);
        return;
      }
      setError(null);
      setSuccess(true);
      formRef.current?.reset();
    });
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
      >
        Invite member
      </button>

      <Modal open={isOpen} onClose={close} title="Invite a member">
        <form ref={formRef} action={handleSubmit} className="mt-4 flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="invite-email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="invite-email"
              name="email"
              type="email"
              required
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-900"
              placeholder="teammate@example.com"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}
          {success && (
            <p className="text-sm text-green-600">
              Invite sent. They&apos;ll get an email to set their password.
            </p>
          )}

          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={close}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-900"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded-lg bg-blue-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-800 disabled:opacity-50"
            >
              {isPending ? "Sending…" : "Send invite"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
