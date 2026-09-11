"use client";

import { useState, FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/Button";
import { Field, Input } from "@/components/Input";
import { Card, Callout } from "@/components/Card";
import { KnowledgePointPicker } from "@/components/KnowledgePointPicker";

type QuestionType = "SINGLE_CHOICE" | "MULTIPLE_CHOICE" | "TRUE_FALSE" | "SHORT_ANSWER" | "NUMERICAL";
type Difficulty = "RECOGNITION" | "COMPREHENSION" | "APPLICATION" | "ADVANCED_APPLICATION";

interface OptionDraft {
  content: string;
  is_correct: boolean;
}

const CHOICE_TYPES: QuestionType[] = ["SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE"];

export default function CreateQuestionPage() {
  const [knowledgePointId, setKnowledgePointId] = useState("");
  const [content, setContent] = useState("");
  const [type, setType] = useState<QuestionType>("SINGLE_CHOICE");
  const [difficulty, setDifficulty] = useState<Difficulty>("RECOGNITION");
  const [explanation, setExplanation] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [options, setOptions] = useState<OptionDraft[]>([
    { content: "", is_correct: true },
    { content: "", is_correct: false },
  ]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const needsOptions = CHOICE_TYPES.includes(type);

  function updateOption(index: number, patch: Partial<OptionDraft>) {
    setOptions((prev) => prev.map((o, i) => (i === index ? { ...o, ...patch } : o)));
  }

  function toggleCorrect(index: number) {
    setOptions((prev) =>
      prev.map((o, i) => {
        if (type === "SINGLE_CHOICE" || type === "TRUE_FALSE") {
          return { ...o, is_correct: i === index };
        }
        return i === index ? { ...o, is_correct: !o.is_correct } : o;
      })
    );
  }

  function addOption() {
    setOptions((prev) => [...prev, { content: "", is_correct: false }]);
  }

  function removeOption(index: number) {
    setOptions((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!knowledgePointId) {
      setError("Vui lòng chọn đầy đủ Môn học → Knowledge point.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        content,
        type,
        difficulty,
        knowledge_point_id: knowledgePointId,
        explanation,
        correct_answer: needsOptions ? "" : correctAnswer,
        options: needsOptions
          ? options
              .filter((o) => o.content.trim())
              .map((o, idx) => ({ content: o.content, is_correct: o.is_correct, order: idx + 1 }))
          : [],
      };
      await api.post("/api/v1/questions", payload);
      setSuccess(true);
      setContent("");
      setExplanation("");
      setCorrectAnswer("");
      setOptions([
        { content: "", is_correct: true },
        { content: "", is_correct: false },
      ]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Không thể tạo câu hỏi.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-serif text-2xl text-ink">Tạo câu hỏi</h1>
      <p className="mt-1 text-sm text-muted">Câu hỏi sẽ ở trạng thái DRAFT — cần chuyển PUBLISHED trước khi thêm vào đề.</p>

      <Card className="mt-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <KnowledgePointPicker value={knowledgePointId} onChange={setKnowledgePointId} />

          <Field label="Nội dung câu hỏi">
            <textarea
              required
              className="min-h-[90px] w-full rounded border border-line px-3 py-2 text-sm text-ink focus:border-flask-500"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Loại câu hỏi">
              <select
                className="h-10 w-full rounded border border-line bg-white px-3 text-sm"
                value={type}
                onChange={(e) => setType(e.target.value as QuestionType)}
              >
                <option value="SINGLE_CHOICE">Một đáp án đúng</option>
                <option value="MULTIPLE_CHOICE">Nhiều đáp án đúng</option>
                <option value="TRUE_FALSE">Đúng / Sai</option>
                <option value="SHORT_ANSWER">Tự luận ngắn</option>
                <option value="NUMERICAL">Số</option>
              </select>
            </Field>
            <Field label="Độ khó">
              <select
                className="h-10 w-full rounded border border-line bg-white px-3 text-sm"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as Difficulty)}
              >
                <option value="RECOGNITION">Nhận biết</option>
                <option value="COMPREHENSION">Thông hiểu</option>
                <option value="APPLICATION">Vận dụng</option>
                <option value="ADVANCED_APPLICATION">Vận dụng cao</option>
              </select>
            </Field>
          </div>

          {needsOptions ? (
            <div>
              <p className="mb-2 text-sm text-muted">Lựa chọn (tick vào ô để đánh dấu đáp án đúng)</p>
              <div className="flex flex-col gap-2">
                {options.map((opt, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <input type="checkbox" checked={opt.is_correct} onChange={() => toggleCorrect(idx)} />
                    <Input
                      value={opt.content}
                      onChange={(e) => updateOption(idx, { content: e.target.value })}
                      placeholder={`Lựa chọn ${idx + 1}`}
                    />
                    {options.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeOption(idx)}
                        className="text-sm text-muted hover:text-danger"
                      >
                        Xóa
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button type="button" onClick={addOption} className="mt-2 text-sm text-flask-500 hover:underline">
                + Thêm lựa chọn
              </button>
            </div>
          ) : (
            <Field label="Đáp án đúng">
              <Input required value={correctAnswer} onChange={(e) => setCorrectAnswer(e.target.value)} />
            </Field>
          )}

          <Field label="Giải thích (tùy chọn)">
            <textarea
              className="min-h-[60px] w-full rounded border border-line px-3 py-2 text-sm text-ink focus:border-flask-500"
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
            />
          </Field>

          {error && <Callout tone="error">{error}</Callout>}
          {success && <Callout tone="success">Đã tạo câu hỏi (trạng thái DRAFT).</Callout>}

          <Button type="submit" disabled={submitting}>
            {submitting ? "Đang lưu…" : "Tạo câu hỏi"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
