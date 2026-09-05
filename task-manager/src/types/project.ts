export type ProjectStatus = "not_started" | "in_progress" | "on_hold" | "completed";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  due_date: string | null;
  owner_id: string | null;
  created_at: string;
}
