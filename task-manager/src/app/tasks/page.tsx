import { Header } from "@/components/dashboard/Header";
import { TaskList } from "@/components/project/TaskList";
import { createClient } from "@/lib/supabase/server";
import type { Profile } from "@/types/profile";
import type { Task } from "@/types/task";

const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export default async function AllTasksPage() {
  if (!isSupabaseConfigured) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black">
        <Header />
        <main className="mx-auto max-w-6xl px-6 py-10">
          <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
            Supabase isn&apos;t configured yet. Set{" "}
            <code className="font-mono">NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
            <code className="font-mono">NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in{" "}
            <code className="font-mono">.env.local</code> to load tasks.
          </div>
        </main>
      </div>
    );
  }

  const supabase = await createClient();

  const [
    {
      data: { user },
    },
    { data: tasksData },
    { data: profilesData },
  ] = await Promise.all([
    supabase.auth.getUser(),
    supabase
      .from("tasks")
      .select("*, projects(name)")
      .order("due_date", { ascending: true, nullsFirst: false })
      .order("created_at", { ascending: false }),
    supabase.from("profiles").select("id, email").order("email"),
  ]);

  const tasks = (tasksData ?? []).map((row) => {
    const { projects: relatedProject, ...task } = row;
    return { ...task, project_name: relatedProject?.name ?? "Unknown project" } as Task & {
      project_name: string;
    };
  });
  const members = (profilesData ?? []) as Profile[];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <Header userEmail={user?.email} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
          <p className="mt-1 text-sm text-black/60 dark:text-white/60">
            Every task across all of your projects.
          </p>
        </div>

        <TaskList tasks={tasks} members={members} emptyMessage="No tasks yet." />
      </main>
    </div>
  );
}
