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
      className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 transition-shadow hover:shadow-sm hover:border-blue-200"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-slate-900">{project.name}</h3>
        <StatusBadge status={project.status} />
      </div>

      {project.description && (
        <p className="line-clamp-2 text-sm text-slate-500">{project.description}</p>
      )}

      {dueDate && <p className="text-xs text-slate-400">Due {dueDate}</p>}
    </Link>
  );
}
