import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

export function DesignIntent() {
  const [docs, setDocs] = useState<Record<string, string> | null>(null);
  useEffect(() => {
    getJSON<Record<string, string>>("/api/intent").then(setDocs);
  }, []);

  if (!docs || Object.keys(docs).length === 0) {
    return <EmptyState>아직 의도 산출물이 없습니다 (페이즈 01–05).</EmptyState>;
  }
  return (
    <div className="markdown">
      {Object.entries(docs).map(([name, body]) => (
        <details key={name} open={name.startsWith("01")}>
          <summary>
            <strong>{name}</strong>
          </summary>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{body}</ReactMarkdown>
        </details>
      ))}
    </div>
  );
}
