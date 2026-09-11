"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";

const NAV = [
  { href: "/teacher/dashboard", label: "Tổng quan" },
  { href: "/teacher/questions/create", label: "Tạo câu hỏi" },
  { href: "/teacher/exams/create", label: "Tạo đề thi" },
];

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) router.replace("/login");
    else if (user.role === "STUDENT") router.replace("/student/dashboard");
  }, [user, loading, router]);

  if (loading || !user) {
    return <div className="flex min-h-screen items-center justify-center text-muted">Đang tải…</div>;
  }

  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar items={NAV} />
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
