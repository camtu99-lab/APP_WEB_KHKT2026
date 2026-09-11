"use client";

import { useState, FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/Button";
import { Field, Input } from "@/components/Input";
import { Card, Callout } from "@/components/Card";

interface QuestionOption {
  id: string;
  content: string;
  is_correct: boolean;
  order: number;
}

interface QuestionSummary {
  id: string;
  content: string;
  type: string;
  options: QuestionOption[];
}

interface ExamQuestion {
  id: string;
  question_id: string;
  order: number;
  points: number;
}

interface ExamDetail {
  id: string;
  title: string;
  duration_minutes: number;
  status: string;
  exam_questions: ExamQuestion[];
}

export default function CreateExamPage() {
  const [title, setTitle] = useState("");
  const [duration, setDuration] = useState(15);
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<QuestionSummary[]>([]);
  const [searching, setSearching] = useState(false);
  const [published, setPublished] = useState(false);

  async function handleCreateExam(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const created = await api.post<ExamDetail>("/api/v1/exams", { title, duration_minutes: duration });
      setExam(created);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể tạo đề thi.");
    } finally {
      setCreating(false);
    }
  }

  async function searchQuestions() {
    setSearching(true);
    try {
      const qs = await api.get<QuestionSummary[]>(
        `/api/v1/questions?status_filter=PUBLISHED${keyword ? `&keyword=${encodeURIComponent(keyword)}` : ""}`
      );
      setResults(qs);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không tìm được câu hỏi.");
    } finally {
      setSearching(false);
    }
  }

  async function addQuestion(questionId: string) {
    if (!exam) return;
    try {
      const updated = await api.post<ExamDetail>(`/api/v1/exams/${exam.id}/questions`, {
        question_id: questionId,
        order: exam.exam_questions.length + 1,
        points: 1,
      });
      setExam(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể thêm câu hỏi vào đề.");
    }
  }

  async function publishExam() {
    if (!exam) return;
    setError(null);
    try {
      await api.post(`/api/v1/exams/${exam.id}/publish`);
      setPublished(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể publish đề thi.");
    }
  }

  const addedIds = new Set(exam?.exam_questions.map((eq) => eq.question_id));

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-serif text-2xl text-ink">Tạo đề thi</h1>

      {!exam && (
        <Card className="mt-6">
          <form onSubmit={handleCreateExam} className="flex flex-col gap-4">
            <Field label="Tiêu đề đề thi">
              <Input required value={title} onChange={(e) => setTitle(e.target.value)} />
            </Field>
            <Field label="Thời gian làm bài (phút)">
              <Input
                type="number"
                min={1}
                max={300}
                required
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </Field>
            {error && <Callout tone="error">{error}</Callout>}
            <Button type="submit" disabled={creating}>
              {creating ? "Đang tạo…" : "Tạo đề (DRAFT)"}
            </Button>
          </form>
        </Card>
      )}

      {exam && (
        <div className="mt-6 flex flex-col gap-5">
          <Card>
            <p className="font-medium text-ink">{exam.title}</p>
            <p className="text-sm text-muted">
              {exam.duration_minutes} phút · {exam.exam_questions.length} câu hỏi đã thêm
            </p>
          </Card>

          {!published && (
            <>
              <Card>
                <p className="mb-3 text-sm text-muted">Tìm câu hỏi đã PUBLISHED để thêm vào đề</p>
                <div className="flex gap-2">
                  <Input
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Từ khóa nội dung câu hỏi…"
                  />
                  <Button type="button" variant="secondary" onClick={searchQuestions} disabled={searching}>
                    {searching ? "Đang tìm…" : "Tìm"}
                  </Button>
                </div>

                <div className="mt-4 flex flex-col gap-2">
                  {results.map((q) => (
                    <div key={q.id} className="flex items-center justify-between rounded border border-line p-3">
                      <p className="text-sm text-ink">{q.content}</p>
                      <Button
                        type="button"
                        variant="secondary"
                        disabled={addedIds.has(q.id)}
                        onClick={() => addQuestion(q.id)}
                      >
                        {addedIds.has(q.id) ? "Đã thêm" : "Thêm"}
                      </Button>
                    </div>
                  ))}
                </div>
              </Card>

              {error && <Callout tone="error">{error}</Callout>}

              <Button onClick={publishExam} disabled={exam.exam_questions.length === 0}>
                Publish đề thi ({exam.exam_questions.length} câu hỏi)
              </Button>
            </>
          )}

          {published && <Callout tone="success">Đề thi đã được publish — học sinh có thể làm bài ngay.</Callout>}
        </div>
      )}
    </div>
  );
}
