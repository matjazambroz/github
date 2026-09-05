import Link from "next/link";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { formatDueDate } from "@/lib/due-date";
import type { Project } from "@/types/project";

export function ProjectCard({ project }: { project: Project }) {
  const dueDate = project.due_date
    ? formatDueDate(project.due_date, { includeYear: true })
    : null;

  return (
    <Link
      href={`/projects/${project.id}`}
      className="flex flex-col gap-3 rounded-xl border border-black/10 bg-white p-5 transition-shadow hover:shadow-sm dark:border-white/10 dark:bg-white/[0.03]"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium">{project.name}</h3>
        <StatusBadge status={project.status} />
      </div>

      {project.description && (
        <p className="line-clamp-2 text-sm text-black/60 dark:text-white/60">
          {project.description}
        </p>
      )}

      {dueDate && (
        <p className="text-xs text-black/40 dark:text-white/40">Due {dueDate}</p>
      )}
    </Link>
  );
}
