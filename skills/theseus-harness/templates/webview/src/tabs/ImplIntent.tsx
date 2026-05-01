import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

type ImplPayload = { impl: string | null; quality: string | null };

export function ImplIntent() {
  const [data, setData] = useState<ImplPayload | null>(null);
  useEffect(() => {
    getJSON<ImplPayload>("/api/impl").then(setData);
  }, []);

  if (!data || (!data.impl && !data.quality)) {
    return <EmptyState>아직 구현 / 품질 게이트 산출물이 없습니다 (페이즈 08–09).</EmptyState>;
  }
  return (
    <div className="markdown">
      {data.impl && (
        <details open>
          <summary><strong>구현 로그 (08-impl-log.md)</strong></summary>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.impl}</ReactMarkdown>
        </details>
      )}
      {data.quality && (
        <details open>
          <summary><strong>품질 게이트 (09-quality-gate.md)</strong></summary>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.quality}</ReactMarkdown>
        </details>
      )}
    </div>
  );
}
