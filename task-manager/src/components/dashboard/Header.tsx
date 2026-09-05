import Link from "next/link";
import { signOut } from "@/app/actions/auth";

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/tasks", label: "Tasks" },
];

export function Header({ userEmail }: { userEmail?: string | null }) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight text-blue-900">
          TaskFlow
        </Link>

        <nav className="flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-slate-500 transition-colors hover:text-blue-900"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {userEmail ? (
          <div className="flex items-center gap-3">
            <div
              title={userEmail}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-900 text-xs font-medium text-white"
            >
              {userEmail.charAt(0).toUpperCase()}
            </div>
            <form action={signOut}>
              <button
                type="submit"
                className="text-sm font-medium text-slate-500 hover:text-blue-900"
              >
                Sign out
              </button>
            </form>
          </div>
        ) : (
          <Link
            href="/login"
            className="text-sm font-medium text-slate-500 hover:text-blue-900"
          >
            Log in
          </Link>
        )}
      </div>
    </header>
  );
}
