"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";
import type { ProjectStatus } from "@/types/project";

export interface CreateProjectResult {
  error: string | null;
}

export async function createProject(
  formData: FormData,
): Promise<CreateProjectResult> {
  const name = String(formData.get("name") ?? "").trim();
  const description = String(formData.get("description") ?? "").trim();
  const status = String(formData.get("status") ?? "not_started") as ProjectStatus;
  const dueDate = String(formData.get("due_date") ?? "").trim();

  if (!name) {
    return { error: "Project name is required." };
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { error } = await supabase.from("projects").insert({
    name,
    description: description || null,
    status,
    due_date: dueDate || null,
    owner_id: user?.id ?? null,
  });

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/");
  return { error: null };
}
