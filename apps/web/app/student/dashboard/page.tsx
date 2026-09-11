"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card } from "@/components/Card";

interface ExamListItem {
  id: string;
  title: string;
  duration_minutes: number;
  status: string;
}

export default function StudentDashboardPage() {
  const [exams, setExams] = useState<ExamListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<ExamListItem[]>("/api/v1/exams")
      .then(setExams)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="font-serif text-2xl text-ink">Đề thi của bạn</h1>
      <p className="mt-1 text-sm text-muted">Chọn một đề để bắt đầu luyện tập.</p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {loading && <p className="text-sm text-muted">Đang tải danh sách đề…</p>}
        {!loading && exams.length === 0 && (
          <Card className="col-span-full text-sm text-muted">
            Chưa có đề thi nào được publish. Hãy quay lại sau.
          </Card>
        )}
        {exams.map((exam) => (
          <Card key={exam.id} className="flex flex-col gap-3">
            <div>
              <p className="font-medium text-ink">{exam.title}</p>
              <p className="text-sm text-muted">{exam.duration_minutes} phút</p>
            </div>
            <Link
              href={`/student/exams/${exam.id}`}
              className="mt-auto inline-block rounded bg-flask-500 px-3 py-2 text-center text-sm text-white hover:bg-flask-600"
            >
              Bắt đầu làm bài
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
