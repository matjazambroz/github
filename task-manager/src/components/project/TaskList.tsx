import { AssigneeSelect } from "@/components/project/AssigneeSelect";
import { DeleteTaskButton } from "@/components/project/DeleteTaskButton";
import { EditTaskButton } from "@/components/project/EditTaskButton";
import { TaskStatusSelect } from "@/components/project/TaskStatusSelect";
import { formatDueDate, getDueUrgency } from "@/lib/due-date";
import type { Profile } from "@/types/profile";
import type { Task } from "@/types/task";

const DUE_DATE_STYLES = {
  overdue: "text-red-600 dark:text-red-400",
  due_soon: "text-amber-600 dark:text-amber-400",
  none: "text-black/40 dark:text-white/40",
};

const DUE_DATE_LABELS = {
  overdue: "Overdue",
  due_soon: "Due soon",
};

export function TaskList({
  tasks,
  projectId,
  members,
}: {
  tasks: Task[];
  projectId: string;
  members: Profile[];
}) {
  if (tasks.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-black/15 p-10 text-center dark:border-white/15">
        <p className="text-sm text-black/60 dark:text-white/60">
          No tasks yet. Add the first task for this project.
        </p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-black/10 rounded-xl border border-black/10 bg-white dark:divide-white/10 dark:border-white/10 dark:bg-white/[0.03]">
      {tasks.map((task) => {
        const dueDate = task.due_date ? formatDueDate(task.due_date) : null;
        const urgency = getDueUrgency(task.due_date, task.status);
        return (
          <li key={task.id} className="flex items-center justify-between gap-4 p-4">
            <div className="min-w-0">
              <p className="truncate font-medium">{task.title}</p>
              {task.description && (
                <p className="mt-0.5 truncate text-sm text-black/60 dark:text-white/60">
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
                projectId={projectId}
                assigneeId={task.assignee_id}
                members={members}
              />
              <TaskStatusSelect taskId={task.id} projectId={projectId} status={task.status} />
              <div className="flex items-center gap-2 border-l border-black/10 pl-3 dark:border-white/10">
                <EditTaskButton task={task} projectId={projectId} />
                <DeleteTaskButton
                  taskId={task.id}
                  projectId={projectId}
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
