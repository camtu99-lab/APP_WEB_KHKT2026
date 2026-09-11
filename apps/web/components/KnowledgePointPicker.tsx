"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Field, Input } from "@/components/Input";

interface Item {
  id: string;
  name: string;
}

async function safeList<T>(path: string): Promise<T[]> {
  try {
    return await api.get<T[]>(path);
  } catch {
    return [];
  }
}

export function KnowledgePointPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (knowledgePointId: string) => void;
}) {
  const [subjects, setSubjects] = useState<Item[]>([]);
  const [grades, setGrades] = useState<Item[]>([]);
  const [chapters, setChapters] = useState<Item[]>([]);
  const [lessons, setLessons] = useState<Item[]>([]);
  const [knowledgePoints, setKnowledgePoints] = useState<Item[]>([]);

  const [subjectId, setSubjectId] = useState("");
  const [gradeId, setGradeId] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [lessonId, setLessonId] = useState("");

  useEffect(() => {
    safeList<Item>("/api/v1/subjects").then(setSubjects);
  }, []);

  useEffect(() => {
    setGrades([]);
    setGradeId("");
    if (!subjectId) return;
    safeList<Item>(`/api/v1/grades?subject_id=${subjectId}`).then(setGrades);
  }, [subjectId]);

  useEffect(() => {
    setChapters([]);
    setChapterId("");
    if (!gradeId) return;
    safeList<Item>(`/api/v1/chapters?grade_id=${gradeId}`).then(setChapters);
  }, [gradeId]);

  useEffect(() => {
    setLessons([]);
    setLessonId("");
    if (!chapterId) return;
    safeList<Item>(`/api/v1/lessons?chapter_id=${chapterId}`).then(setLessons);
  }, [chapterId]);

  useEffect(() => {
    setKnowledgePoints([]);
    onChange("");
    if (!lessonId) return;
    safeList<Item>(`/api/v1/knowledge-points?lesson_id=${lessonId}`).then(setKnowledgePoints);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId]);

  function selectClass() {
    return "h-10 w-full rounded border border-line bg-white px-3 text-sm text-ink focus:border-flask-500";
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Field label="Môn học">
        <select className={selectClass()} value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
          <option value="">— Chọn —</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Lớp">
        <select className={selectClass()} value={gradeId} onChange={(e) => setGradeId(e.target.value)} disabled={!subjectId}>
          <option value="">— Chọn —</option>
          {grades.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Chương">
        <select className={selectClass()} value={chapterId} onChange={(e) => setChapterId(e.target.value)} disabled={!gradeId}>
          <option value="">— Chọn —</option>
          {chapters.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Bài học">
        <select className={selectClass()} value={lessonId} onChange={(e) => setLessonId(e.target.value)} disabled={!chapterId}>
          <option value="">— Chọn —</option>
          {lessons.map((l) => (
            <option key={l.id} value={l.id}>
              {l.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Knowledge point">
        <select className={selectClass()} value={value} onChange={(e) => onChange(e.target.value)} disabled={!lessonId}>
          <option value="">— Chọn —</option>
          {knowledgePoints.map((k) => (
            <option key={k.id} value={k.id}>
              {k.name}
            </option>
          ))}
        </select>
      </Field>
    </div>
  );
}
