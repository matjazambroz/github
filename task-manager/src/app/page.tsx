import { Header } from "@/components/dashboard/Header";
import { NewProjectButton } from "@/components/dashboard/NewProjectButton";
import { ProjectList } from "@/components/dashboard/ProjectList";
import { createClient } from "@/lib/supabase/server";
import type { Project } from "@/types/project";

const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

async function getDashboardData(): Promise<{
  projects: Project[];
  error: string | null;
  userEmail: string | null;
}> {
  if (!isSupabaseConfigured) {
    return { projects: [], error: null, userEmail: null };
  }

  const supabase = await createClient();

  const [{ data: userData }, { data: projectsData, error }] = await Promise.all([
    supabase.auth.getUser(),
    supabase.from("projects").select("*").order("created_at", { ascending: false }),
  ]);

  return {
    projects: projectsData ?? [],
    error: error?.message ?? null,
    userEmail: userData.user?.email ?? null,
  };
}

export default async function DashboardPage() {
  const { projects, error, userEmail } = await getDashboardData();

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
          <NewProjectButton />
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

        <ProjectList projects={projects} />
      </main>
    </div>
  );
}
