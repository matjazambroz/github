-- The dashboard now sits behind Supabase auth, so require a signed-in user
-- for reading and creating projects instead of allowing anonymous access.
drop policy if exists "Anyone can view projects" on public.projects;
drop policy if exists "Anyone can create projects" on public.projects;

create policy "Authenticated users can view projects"
  on public.projects for select
  to authenticated
  using (true);

create policy "Authenticated users can create projects"
  on public.projects for insert
  to authenticated
  with check (true);
