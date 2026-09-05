-- Projects table backing the dashboard's project list.
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  status text not null default 'not_started'
    check (status in ('not_started', 'in_progress', 'on_hold', 'completed')),
  due_date date,
  owner_id uuid references auth.users (id) on delete set null,
  created_at timestamptz not null default now()
);

alter table public.projects enable row level security;

create policy "Anyone can view projects"
  on public.projects for select
  using (true);

create policy "Anyone can create projects"
  on public.projects for insert
  with check (true);

create policy "Owners can update their projects"
  on public.projects for update
  using (auth.uid() = owner_id);

create policy "Owners can delete their projects"
  on public.projects for delete
  using (auth.uid() = owner_id);
