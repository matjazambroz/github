import { AuthForm } from "@/components/auth/AuthForm";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-1 items-center justify-center bg-slate-50 px-6">
      <div className="flex flex-col items-center gap-6">
        <span className="text-lg font-semibold tracking-tight">TaskFlow</span>
        <AuthForm />
      </div>
    </div>
  );
}
