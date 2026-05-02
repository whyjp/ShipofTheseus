import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

// v0.2.1 회귀 수정 (Cursor Bugbot PR#1 지적):
// inputs.json 은 score.py 의 *입력* (test_pass_rate, coverage 등) — `score` 필드 없음.
// 차트가 항상 빈 상태였던 원인. score.py --out 으로 산출되는 score.json 을 읽는다.
type ScoreOutput = {
  score: number;
  raw_score: number;
  sub_scores: Record<string, number | null>;
  caps_applied: string[];
  dip_violation: boolean;
  passes_threshold: boolean;
  regression_triggered?: boolean;
};

type Sprint = {
  sprint: string;
  report: string | null;
  inputs: any | null;
  score: ScoreOutput | null;
  bisect: string | null;
};

export function Sprints() {
  const [sprints, setSprints] = useState<Sprint[] | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  useEffect(() => {
    getJSON<Sprint[]>("/api/sprints").then(setSprints);
  }, []);

  if (!sprints || sprints.length === 0) {
    return <EmptyState>아직 스프린트 결과가 없습니다 (페이즈 10).</EmptyState>;
  }

  const chartData = sprints
    .map((s) => ({
      sprint: s.sprint,
      score: s.score?.score ?? null,
    }))
    .filter((d): d is { sprint: string; score: number } => d.score != null);

  return (
    <div>
      {chartData.length > 0 && (
        <div style={{ height: 240, marginBottom: 24 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sprint" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {sprints.map((s) => {
        const score = s.score?.score;
        const isOpen = open === s.sprint;
        return (
          <div className="sprint-row" key={s.sprint}>
            <h3
              style={{ cursor: "pointer" }}
              onClick={() => setOpen(isOpen ? null : s.sprint)}
            >
              스프린트 {s.sprint}
              {score != null && (
                <span
                  className={`score-pill ${score >= 0.9 ? "good" : "bad"}`}
                  style={{ marginLeft: 12 }}
                >
                  {score.toFixed(3)}
                </span>
              )}
              {s.bisect && (
                <span className="score-pill bad" style={{ marginLeft: 8 }}>
                  회귀 바이섹트
                </span>
              )}
            </h3>
            {isOpen && (
              <div className="markdown">
                {s.report && (
                  <details open>
                    <summary><strong>report.md</strong></summary>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{s.report}</ReactMarkdown>
                  </details>
                )}
                {s.bisect && (
                  <details open>
                    <summary><strong>bisect.md</strong></summary>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{s.bisect}</ReactMarkdown>
                  </details>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
