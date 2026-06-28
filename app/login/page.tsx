import { Suspense } from "react";
import { LoginForm } from "@/src/components/login-form";

export const metadata = {
  title: "Anmelden · Pharma QRM",
};

export default function LoginPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-[var(--background)] px-5 py-12">
      <Suspense fallback={null}>
        <LoginForm />
      </Suspense>
    </main>
  );
}
