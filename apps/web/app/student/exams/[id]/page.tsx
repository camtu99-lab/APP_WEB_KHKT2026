"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/Button";
import { Card, Callout } from "@/components/Card";

interface AttemptQuestionView {
  question_id: string;
  content: string;
  type: "SINGLE_CHOICE" | "MULTIPLE_CHOICE" | "TRUE_FALSE" | "SHORT_ANSWER" | "NUMERICAL";
  points: number;
  options: { id: string; content: string; order: number }[];
}

interface AttemptStartResponse {
  attempt_id: string;
  exam_id: string;
  status: string;
  started_at: string;
  duration_minutes: number;
  questions: AttemptQuestionView[];
}

interface AnswerState {
  selected_option_ids: string[];
  answer_text: string;
}

export default function TakeExamPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const startedRef = useRef(false);

  const [attempt, setAttempt] = useState<AttemptStartResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, AnswerState>>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    api
      .post<AttemptStartResponse>(`/api/v1/exams/${params.id}/start`)
      .then((data) => {
        setAttempt(data);
        const endTime = new Date(data.started_at).getTime() + data.duration_minutes * 60_000;
        setSecondsLeft(Math.max(0, Math.round((endTime - Date.now()) / 1000)));
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Không thể bắt đầu làm bài."));
  }, [params.id]);

  const submit = useCallback(async () => {
    if (!attempt || submitting) return;
    setSubmitting(true);
    try {
      const payload = {
        answers: Object.entries(answers).map(([question_id, a]) => ({
          question_id,
          selected_option_ids: a.selected_option_ids,
          answer_text: a.answer_text,
        })),
      };
      await api.post(`/api/v1/attempts/${attempt.attempt_id}/submit`, payload);
      router.push(`/student/results/${attempt.attempt_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể nộp bài, vui lòng thử lại.");
      setSubmitting(false);
    }
  }, [attempt, answers, submitting, router]);

  useEffect(() => {
    if (secondsLeft === null) return;
    if (secondsLeft <= 0) {
      submit();
      return;
    }
    const timer = setTimeout(() => setSecondsLeft((s) => (s !== null ? s - 1 : s)), 1000);
    return () => clearTimeout(timer);
  }, [secondsLeft, submit]);

  function selectSingle(questionId: string, optionId: string) {
    setAnswers((prev) => ({ ...prev, [questionId]: { selected_option_ids: [optionId], answer_text: "" } }));
  }

  function toggleMultiple(questionId: string, optionId: string) {
    setAnswers((prev) => {
      const current = prev[questionId]?.selected_option_ids || [];
      const next = current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId];
      return { ...prev, [questionId]: { selected_option_ids: next, answer_text: "" } };
    });
  }

  function setText(questionId: string, text: string) {
    setAnswers((prev) => ({ ...prev, [questionId]: { selected_option_ids: [], answer_text: text } }));
  }

  if (error && !attempt) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <Callout tone="error">{error}</Callout>
      </div>
    );
  }

  if (!attempt) {
    return <div className="p-8 text-sm text-muted">Đang chuẩn bị đề thi…</div>;
  }

  const minutes = secondsLeft !== null ? Math.floor(secondsLeft / 60) : 0;
  const seconds = secondsLeft !== null ? secondsLeft % 60 : 0;

  return (
    <div className="min-h-screen bg-paper">
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-line bg-white px-8 py-4">
        <h1 className="font-serif text-xl text-ink">Đang làm bài</h1>
        <div
          className={`rounded px-3 py-1.5 text-sm font-medium ${
            secondsLeft !== null && secondsLeft < 60 ? "bg-[#F7E9E5] text-danger" : "bg-flask-50 text-flask-600"
          }`}
        >
          {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
        </div>
      </div>

      <div className="mx-auto max-w-2xl px-4 py-8">
        {error && (
          <div className="mb-4">
            <Callout tone="error">{error}</Callout>
          </div>
        )}

        <div className="flex flex-col gap-5">
          {attempt.questions.map((q, idx) => (
            <Card key={q.question_id}>
              <p className="mb-3 text-sm text-muted">
                Câu {idx + 1} · {q.points} điểm
              </p>
              <p className="mb-4 text-ink">{q.content}</p>

              {(q.type === "SINGLE_CHOICE" || q.type === "TRUE_FALSE") &&
                q.options.map((opt) => (
                  <label key={opt.id} className="mb-2 flex items-center gap-2 text-sm text-ink">
                    <input
                      type="radio"
                      name={q.question_id}
                      checked={answers[q.question_id]?.selected_option_ids?.[0] === opt.id}
                      onChange={() => selectSingle(q.question_id, opt.id)}
                    />
                    {opt.content}
                  </label>
                ))}

              {q.type === "MULTIPLE_CHOICE" &&
                q.options.map((opt) => (
                  <label key={opt.id} className="mb-2 flex items-center gap-2 text-sm text-ink">
                    <input
                      type="checkbox"
                      checked={answers[q.question_id]?.selected_option_ids?.includes(opt.id) || false}
                      onChange={() => toggleMultiple(q.question_id, opt.id)}
                    />
                    {opt.content}
                  </label>
                ))}

              {(q.type === "SHORT_ANSWER" || q.type === "NUMERICAL") && (
                <input
                  className="h-10 w-full rounded border border-line px-3 text-sm"
                  placeholder="Nhập câu trả lời…"
                  value={answers[q.question_id]?.answer_text || ""}
                  onChange={(e) => setText(q.question_id, e.target.value)}
                />
              )}
            </Card>
          ))}
        </div>

        <Button className="mt-6 w-full" disabled={submitting} onClick={submit}>
          {submitting ? "Đang nộp bài…" : "Nộp bài"}
        </Button>
      </div>
    </div>
  );
}
