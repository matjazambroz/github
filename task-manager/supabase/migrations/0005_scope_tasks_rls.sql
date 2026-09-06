-- The original task policies allowed any authenticated user to read, create,
-- update, or delete any task on any project. Scope mutations to the task's
-- project owner, with the assignee also allowed to update (e.g. status)
-- their own assigned tasks.
drop policy if exists "Authenticated users can create tasks" on public.tasks;
drop policy if exists "Authenticated users can update tasks" on public.tasks;
drop policy if exists "Authenticated users can delete tasks" on public.tasks;

create policy "Project owners can create tasks"
  on public.tasks for insert
  to authenticated
  with check (
    exists (
      select 1 from public.projects p
      where p.id = project_id and p.owner_id = auth.uid()
    )
  );

create policy "Project owners and assignees can update tasks"
  on public.tasks for update
  to authenticated
  using (
    assignee_id = auth.uid()
    or exists (
      select 1 from public.projects p
      where p.id = project_id and p.owner_id = auth.uid()
    )
  );

create policy "Project owners can delete tasks"
  on public.tasks for delete
  to authenticated
  using (
    exists (
      select 1 from public.projects p
      where p.id = project_id and p.owner_id = auth.uid()
    )
  );
