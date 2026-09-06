"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

const isSupabaseConfigured =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL && !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export interface InviteMemberResult {
  error: string | null;
}

export async function inviteMember(formData: FormData): Promise<InviteMemberResult> {
  const email = String(formData.get("email") ?? "").trim();

  if (!email) {
    return { error: "Email is required." };
  }

  if (!isSupabaseConfigured) {
    return { error: "Supabase isn't configured yet." };
  }

  if (!process.env.SUPABASE_SERVICE_ROLE_KEY) {
    return {
      error: "Inviting users isn't configured yet (missing SUPABASE_SERVICE_ROLE_KEY).",
    };
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return { error: "You must be signed in to invite someone." };
  }

  const admin = createAdminClient();
  const { error } = await admin.auth.admin.inviteUserByEmail(email);

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/");
  return { error: null };
}
