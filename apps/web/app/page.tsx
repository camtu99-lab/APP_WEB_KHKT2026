"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
    } else if (user.role === "STUDENT") {
      router.replace("/student/dashboard");
    } else {
      router.replace("/teacher/dashboard");
    }
  }, [user, loading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center text-muted">
      <p>Đang tải Chemgenie…</p>
    </div>
  );
}
