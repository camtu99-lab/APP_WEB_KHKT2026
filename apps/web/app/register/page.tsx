"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth, Role } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/Button";
import { Field, Input } from "@/components/Input";
import { Card, Callout } from "@/components/Card";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("STUDENT");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, fullName, password, role);
      setSuccess(true);
      setTimeout(() => router.push("/login"), 1200);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể đăng ký, vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-4">
      <Card className="w-full max-w-sm">
        <h1 className="font-serif text-2xl text-ink">Tạo tài khoản</h1>
        <p className="mb-6 mt-1 text-sm text-muted">Bắt đầu học cùng Chemgenie</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Field label="Họ và tên">
            <Input required value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </Field>
          <Field label="Email">
            <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Field label="Mật khẩu">
            <Input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </Field>
          <Field label="Vai trò">
            <div className="flex gap-2">
              {(["STUDENT", "TEACHER"] as Role[]).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className={`flex-1 rounded border px-3 py-2 text-sm ${
                    role === r ? "border-flask-500 bg-flask-50 text-flask-600" : "border-line text-muted"
                  }`}
                >
                  {r === "STUDENT" ? "Học sinh" : "Giáo viên"}
                </button>
              ))}
            </div>
          </Field>

          {error && <Callout tone="error">{error}</Callout>}
          {success && <Callout tone="success">Đăng ký thành công, đang chuyển tới trang đăng nhập…</Callout>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Đang tạo tài khoản…" : "Đăng ký"}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-muted">
          Đã có tài khoản?{" "}
          <Link href="/login" className="text-flask-500 hover:underline">
            Đăng nhập
          </Link>
        </p>
      </Card>
    </div>
  );
}
