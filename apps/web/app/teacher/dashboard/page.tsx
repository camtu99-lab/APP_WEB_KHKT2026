"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { Card, Callout } from "@/components/Card";
import { Button } from "@/components/Button";

interface ExamListItem {
  id: string;
  title: string;
  duration_minutes: number;
  status: string;
}

export default function TeacherDashboardPage() {
  const [exams, setExams] = useState<ExamListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [publishingId, setPublishingId] = useState<string | null>(null);

  function load() {
    setLoading(true);
    api
      .get<ExamListItem[]>("/api/v1/exams")
      .then(setExams)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Không tải được danh sách đề."))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function publish(examId: string) {
    setPublishingId(examId);
    try {
      await api.post(`/api/v1/exams/${examId}/publish`);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể publish đề thi.");
    } finally {
      setPublishingId(null);
    }
  }

  return (
    <div>
      <h1 className="font-serif text-2xl text-ink">Tổng quan</h1>
      <p className="mt-1 text-sm text-muted">Danh sách đề thi bạn đã tạo.</p>

      {error && (
        <div className="mt-4">
          <Callout tone="error">{error}</Callout>
        </div>
      )}

      <div className="mt-6 flex flex-col gap-3">
        {loading && <p className="text-sm text-muted">Đang tải…</p>}
        {!loading && exams.length === 0 && (
          <Card className="text-sm text-muted">Chưa có đề thi nào. Vào mục "Tạo đề thi" để bắt đầu.</Card>
        )}
        {exams.map((exam) => (
          <Card key={exam.id} className="flex items-center justify-between">
            <div>
              <p className="font-medium text-ink">{exam.title}</p>
              <p className="text-sm text-muted">
                {exam.duration_minutes} phút ·{" "}
                <span className={exam.status === "PUBLISHED" ? "text-flask-600" : "text-flame-500"}>
                  {exam.status}
                </span>
              </p>
            </div>
            {exam.status === "DRAFT" && (
              <Button variant="secondary" disabled={publishingId === exam.id} onClick={() => publish(exam.id)}>
                {publishingId === exam.id ? "Đang publish…" : "Publish"}
              </Button>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
