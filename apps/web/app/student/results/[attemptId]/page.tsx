"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Card, Callout } from "@/components/Card";

interface AnswerResultView {
  question_id: string;
  is_correct: boolean;
  points_earned: number;
  points_possible: number;
  correct_option_ids: string[];
  correct_answer: string;
  explanation: string;
}

interface AttemptResultResponse {
  attempt_id: string;
  exam_id: string;
  status: string;
  score: number | null;
  max_score: number;
  submitted_at: string | null;
  answers: AnswerResultView[];
}

export default function ExamResultPage() {
  const params = useParams<{ attemptId: string }>();
  const [result, setResult] = useState<AttemptResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<AttemptResultResponse>(`/api/v1/attempts/${params.attemptId}/result`)
      .then(setResult)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Không tải được kết quả."));
  }, [params.attemptId]);

  if (error) return <Callout tone="error">{error}</Callout>;
  if (!result) return <p className="text-sm text-muted">Đang tải kết quả…</p>;

  const percent = result.max_score > 0 ? Math.round(((result.score || 0) / result.max_score) * 100) : 0;

  return (
    <div>
      <Card className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-serif text-2xl text-ink">Kết quả bài làm</h1>
          <p className="mt-1 text-sm text-muted">
            {result.answers.filter((a) => a.is_correct).length}/{result.answers.length} câu đúng
          </p>
        </div>
        <div className="text-right">
          <p className="font-serif text-3xl text-flask-600">
            {result.score}/{result.max_score}
          </p>
          <p className="text-sm text-muted">{percent}%</p>
        </div>
      </Card>

      <div className="flex flex-col gap-4">
        {result.answers.map((a, idx) => (
          <Card key={a.question_id} className={a.is_correct ? "border-flask-100" : "border-[#EFD3CB]"}>
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-ink">Câu {idx + 1}</p>
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  a.is_correct ? "bg-flask-50 text-flask-600" : "bg-[#F7E9E5] text-danger"
                }`}
              >
                {a.is_correct ? "Đúng" : "Sai"} · {a.points_earned}/{a.points_possible} điểm
              </span>
            </div>
            {a.explanation && <p className="mt-2 text-sm text-muted">{a.explanation}</p>}
          </Card>
        ))}
      </div>
    </div>
  );
}
