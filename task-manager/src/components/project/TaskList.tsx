import Link from "next/link";
import { AssigneeSelect } from "@/components/project/AssigneeSelect";
import { DeleteTaskButton } from "@/components/project/DeleteTaskButton";
import { EditTaskButton } from "@/components/project/EditTaskButton";
import { TaskStatusSelect } from "@/components/project/TaskStatusSelect";
import { formatDueDate, getDueUrgency } from "@/lib/due-date";
import type { Profile } from "@/types/profile";
import type { Task } from "@/types/task";

const DUE_DATE_STYLES = {
  overdue: "text-red-600",
  due_soon: "text-amber-600",
  none: "text-slate-400",
};

const DUE_DATE_LABELS = {
  overdue: "Overdue",
  due_soon: "Due soon",
};

export function TaskList({
  tasks,
  members,
  emptyMessage = "No tasks yet. Add the first task for this project.",
}: {
  tasks: (Task & { project_name?: string })[];
  members: Profile[];
  emptyMessage?: string;
}) {
  if (tasks.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 p-10 text-center">
        <p className="text-sm text-slate-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
      {tasks.map((task) => {
        const dueDate = task.due_date ? formatDueDate(task.due_date) : null;
        const urgency = getDueUrgency(task.due_date, task.status);
        return (
          <li key={task.id} className="flex items-center justify-between gap-4 p-4">
            <div className="min-w-0">
              <p className="truncate font-medium">{task.title}</p>
              {task.project_name && (
                <Link
                  href={`/projects/${task.project_id}`}
                  className="text-sm text-slate-500 hover:underline"
                >
                  {task.project_name}
                </Link>
              )}
              {task.description && (
                <p className="mt-0.5 truncate text-sm text-slate-500">
                  {task.description}
                </p>
              )}
              {dueDate && (
                <p className={`mt-0.5 text-xs ${DUE_DATE_STYLES[urgency ?? "none"]}`}>
                  Due {dueDate}
                  {urgency && ` · ${DUE_DATE_LABELS[urgency]}`}
                </p>
              )}
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <AssigneeSelect
                taskId={task.id}
                projectId={task.project_id}
                assigneeId={task.assignee_id}
                members={members}
              />
              <TaskStatusSelect
                taskId={task.id}
                projectId={task.project_id}
                status={task.status}
              />
              <div className="flex items-center gap-2 border-l border-slate-200 pl-3">
                <EditTaskButton task={task} projectId={task.project_id} />
                <DeleteTaskButton
                  taskId={task.id}
                  projectId={task.project_id}
                  taskTitle={task.title}
                />
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
