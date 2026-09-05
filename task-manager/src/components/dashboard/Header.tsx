import Link from "next/link";
import { signOut } from "@/app/actions/auth";

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/tasks", label: "Tasks" },
];

export function Header({ userEmail }: { userEmail?: string | null }) {
  return (
    <header className="border-b border-black/10 bg-white dark:border-white/10 dark:bg-black">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          TaskFlow
        </Link>

        <nav className="flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-black/60 transition-colors hover:text-black dark:text-white/60 dark:hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {userEmail ? (
          <div className="flex items-center gap-3">
            <div
              title={userEmail}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-black/10 text-xs font-medium dark:bg-white/10"
            >
              {userEmail.charAt(0).toUpperCase()}
            </div>
            <form action={signOut}>
              <button
                type="submit"
                className="text-sm font-medium text-black/60 hover:text-black dark:text-white/60 dark:hover:text-white"
              >
                Sign out
              </button>
            </form>
          </div>
        ) : (
          <Link
            href="/login"
            className="text-sm font-medium text-black/60 hover:text-black dark:text-white/60 dark:hover:text-white"
          >
            Log in
          </Link>
        )}
      </div>
    </header>
  );
}
