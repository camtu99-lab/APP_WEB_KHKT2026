"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/Button";
import { Field, Input } from "@/components/Input";
import { Card, Callout } from "@/components/Card";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const user = await login(email, password);
      router.push(user.role === "STUDENT" ? "/student/dashboard" : "/teacher/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể đăng nhập, vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-4">
      <Card className="w-full max-w-sm">
        <h1 className="font-serif text-2xl text-ink">Chemgenie</h1>
        <p className="mb-6 mt-1 text-sm text-muted">Học và luyện thi hóa học THPT</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Field label="Email">
            <Input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ten@truong.edu.vn"
            />
          </Field>
          <Field label="Mật khẩu">
            <Input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </Field>

          {error && <Callout tone="error">{error}</Callout>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Đang đăng nhập…" : "Đăng nhập"}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-muted">
          Chưa có tài khoản?{" "}
          <Link href="/register" className="text-flask-500 hover:underline">
            Đăng ký
          </Link>
        </p>
      </Card>
    </div>
  );
}
