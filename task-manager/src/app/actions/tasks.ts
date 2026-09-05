"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";
import type { TaskStatus } from "@/types/task";

export interface CreateTaskResult {
  error: string | null;
}

export async function createTask(
  projectId: string,
  formData: FormData,
): Promise<CreateTaskResult> {
  const title = String(formData.get("title") ?? "").trim();
  const description = String(formData.get("description") ?? "").trim();
  const dueDate = String(formData.get("due_date") ?? "").trim();
  const assigneeId = String(formData.get("assignee_id") ?? "").trim();

  if (!title) {
    return { error: "Task title is required." };
  }

  const supabase = await createClient();
  const { error } = await supabase.from("tasks").insert({
    project_id: projectId,
    title,
    description: description || null,
    due_date: dueDate || null,
    assignee_id: assigneeId || null,
  });

  if (error) {
    return { error: error.message };
  }

  revalidatePath(`/projects/${projectId}`);
  return { error: null };
}

export async function updateTaskStatus(
  taskId: string,
  projectId: string,
  status: TaskStatus,
) {
  const supabase = await createClient();
  await supabase.from("tasks").update({ status }).eq("id", taskId);
  revalidatePath(`/projects/${projectId}`);
}

export async function updateTaskAssignee(
  taskId: string,
  projectId: string,
  assigneeId: string | null,
) {
  const supabase = await createClient();
  await supabase.from("tasks").update({ assignee_id: assigneeId }).eq("id", taskId);
  revalidatePath(`/projects/${projectId}`);
}
