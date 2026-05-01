import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

/**
 * 모듈 구성도 — 1단계 구현은 plan/06-plan.md 의 마크다운을 렌더하고,
 * 그 안의 "의존 DAG" 코드 블록을 그대로 보여준다.
 * 후속 개선 여지: react-flow 로 노드/엣지를 그래픽 렌더 (계획 파서 추가 후).
 */
export function ModuleMap() {
  const [docs, setDocs] = useState<Record<string, string> | null>(null);
  useEffect(() => {
    getJSON<Record<string, string>>("/api/plan").then(setDocs);
  }, []);

  const planMd = docs?.["06-plan.md"] ?? null;
  if (!planMd) {
    return <EmptyState>아직 계획 산출물이 없습니다 (페이즈 06).</EmptyState>;
  }
  return (
    <div className="markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{planMd}</ReactMarkdown>
    </div>
  );
}
