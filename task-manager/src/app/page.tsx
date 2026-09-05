import { Header } from "@/components/dashboard/Header";
import { InviteMemberButton } from "@/components/dashboard/InviteMemberButton";
import { NewProjectButton } from "@/components/dashboard/NewProjectButton";
import { ProjectList } from "@/components/dashboard/ProjectList";
import { RemindersPanel, type ReminderTask } from "@/components/dashboard/RemindersPanel";
import { createClient } from "@/lib/supabase/server";
import type { Project } from "@/types/project";

const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const REMINDER_WINDOW_DAYS = 3;

async function getDashboardData(): Promise<{
  projects: Project[];
  reminders: ReminderTask[];
  error: string | null;
  userEmail: string | null;
}> {
  if (!isSupabaseConfigured) {
    return { projects: [], reminders: [], error: null, userEmail: null };
  }

  const supabase = await createClient();

  const reminderCutoff = new Date();
  reminderCutoff.setDate(reminderCutoff.getDate() + REMINDER_WINDOW_DAYS);
  const reminderCutoffDate = reminderCutoff.toISOString().slice(0, 10);

  const [{ data: userData }, { data: projectsData, error }, { data: reminderRows }] =
    await Promise.all([
      supabase.auth.getUser(),
      supabase.from("projects").select("*").order("created_at", { ascending: false }),
      supabase
        .from("tasks")
        .select("*, projects(name)")
        .neq("status", "done")
        .not("due_date", "is", null)
        .lte("due_date", reminderCutoffDate)
        .order("due_date", { ascending: true })
        .limit(8),
    ]);

  const reminders: ReminderTask[] = (reminderRows ?? []).map((row) => {
    const { projects: relatedProject, ...task } = row;
    return { ...task, project_name: relatedProject?.name ?? "Unknown project" };
  });

  return {
    projects: projectsData ?? [],
    reminders,
    error: error?.message ?? null,
    userEmail: userData.user?.email ?? null,
  };
}

export default async function DashboardPage() {
  const { projects, reminders, error, userEmail } = await getDashboardData();

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <Header userEmail={userEmail} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
            <p className="mt-1 text-sm text-black/60 dark:text-white/60">
              An overview of every project and its current status.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <InviteMemberButton />
            <NewProjectButton />
          </div>
        </div>

        {!isSupabaseConfigured && (
          <div className="mb-6 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
            Supabase isn&apos;t configured yet. Set{" "}
            <code className="font-mono">NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
            <code className="font-mono">NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in{" "}
            <code className="font-mono">.env.local</code> to load real projects.
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
            Couldn&apos;t load projects: {error}
          </div>
        )}

        <RemindersPanel tasks={reminders} />

        <ProjectList projects={projects} />
      </main>
    </div>
  );
}
