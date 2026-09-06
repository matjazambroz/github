# TaskFlow

A task management application built with Next.js, Tailwind CSS, and Supabase.

## Features

- Dashboard overview with project status and due date reminders
- Project and task creation, editing, and deletion
- Assigning tasks to users, with an "Invite member" flow to add new users
- Email/password auth, with every route protected behind login

## Getting started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create a Supabase project at [supabase.com](https://supabase.com), then copy `.env.example` to `.env.local` and fill in your project's URL, anon key, and service role key (the last one is only needed for the "Invite member" flow, from Settings > API in your Supabase project — keep it server-only, never commit it):

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
