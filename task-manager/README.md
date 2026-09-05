# TaskFlow

A task management application built with Next.js, Tailwind CSS, and Supabase.

## Planned features

- Project and task creation
- Assigning tasks to users
- Due date reminders
- Dashboard overview

The dashboard (header, project list, and "new project" flow) is implemented first; auth, task creation/assignment, and reminders are built on top of it next.

## Getting started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create a Supabase project at [supabase.com](https://supabase.com), then copy `.env.example` to `.env.local` and fill in your project's URL and anon key:

   ```bash
   cp .env.example .env.local
   ```

3. Apply the database schema in `supabase/migrations/` to your Supabase project (via the SQL editor or the Supabase CLI):

   ```bash
   supabase db push
   ```

4. Run the dev server:

   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) to see the dashboard.

Without Supabase credentials configured, the dashboard still renders with an empty project list and a setup notice.

## Tech stack

- [Next.js](https://nextjs.org) (App Router)
- [Tailwind CSS](https://tailwindcss.com)
- [Supabase](https://supabase.com) (auth + Postgres database)
