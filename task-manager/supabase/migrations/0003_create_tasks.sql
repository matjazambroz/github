-- Tasks belonging to a project, shown on the project detail page.
create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects (id) on delete cascade,
  title text not null,
  description text,
  status text not null default 'todo'
    check (status in ('todo', 'in_progress', 'done')),
  due_date date,
  assignee_id uuid references auth.users (id) on delete set null,
  created_at timestamptz not null default now()
);

create index if not exists tasks_project_id_idx on public.tasks (project_id);

alter table public.tasks enable row level security;

create policy "Authenticated users can view tasks"
  on public.tasks for select
  to authenticated
  using (true);

create policy "Authenticated users can create tasks"
  on public.tasks for insert
  to authenticated
  with check (true);

create policy "Authenticated users can update tasks"
  on public.tasks for update
  to authenticated
  using (true);

create policy "Authenticated users can delete tasks"
  on public.tasks for delete
  to authenticated
  using (true);
