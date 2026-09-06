import Link from "next/link";
import { notFound } from "next/navigation";
import { Header } from "@/components/dashboard/Header";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { DeleteProjectButton } from "@/components/project/DeleteProjectButton";
import { EditProjectButton } from "@/components/project/EditProjectButton";
import { NewTaskButton } from "@/components/project/NewTaskButton";
import { TaskList } from "@/components/project/TaskList";
import { createClient } from "@/lib/supabase/server";
import type { Profile } from "@/types/profile";
import type { Task } from "@/types/task";

const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export default async function ProjectDetailPage(props: PageProps<"/projects/[id]">) {
  if (!isSupabaseConfigured) {
    notFound();
  }

  const { id } = await props.params;
  const supabase = await createClient();

  const [
    {
      data: { user },
    },
    { data: project },
    { data: tasksData },
    { data: profilesData },
  ] = await Promise.all([
    supabase.auth.getUser(),
    supabase.from("projects").select("*").eq("id", id).maybeSingle(),
    supabase
      .from("tasks")
      .select("*")
      .eq("project_id", id)
      .order("created_at", { ascending: false }),
    supabase.from("profiles").select("id, email").order("email"),
  ]);

  if (!project) {
    notFound();
  }

  const tasks = (tasksData ?? []) as Task[];
  const members = (profilesData ?? []) as Profile[];

  return (
    <div className="min-h-screen bg-slate-50">
      <Header userEmail={user?.email} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <Link
          href="/"
          className="text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          ← All projects
        </Link>

        <div className="mt-4 mb-8 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold tracking-tight">{project.name}</h1>
              <StatusBadge status={project.status} />
            </div>
            {project.description && (
              <p className="mt-1 text-sm text-slate-500">
                {project.description}
              </p>
            )}
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <EditProjectButton project={project} />
            <DeleteProjectButton projectId={project.id} projectName={project.name} />
            <NewTaskButton projectId={project.id} members={members} />
          </div>
        </div>

        <TaskList tasks={tasks} members={members} />
      </main>
    </div>
  );
}
