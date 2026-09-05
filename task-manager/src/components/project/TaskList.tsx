import { TaskStatusSelect } from "@/components/project/TaskStatusSelect";
import type { Task } from "@/types/task";

function formatDueDate(dueDate: string | null) {
  if (!dueDate) return null;
  return new Date(dueDate).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

export function TaskList({ tasks, projectId }: { tasks: Task[]; projectId: string }) {
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
        const dueDate = formatDueDate(task.due_date);
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
                <p className="mt-0.5 text-xs text-black/40 dark:text-white/40">
                  Due {dueDate}
                </p>
              )}
            </div>
            <TaskStatusSelect taskId={task.id} projectId={projectId} status={task.status} />
          </li>
        );
      })}
    </ul>
  );
}
