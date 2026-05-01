import { useEffect, useState } from "react";

type Timing = {
  started_at_iso: string | null;
  now_iso: string;
  elapsed_seconds: number | null;
};

function formatElapsed(s: number | null): string {
  if (s == null) return "—";
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}시간 ${m}분 ${sec}초`;
  if (m > 0) return `${m}분 ${sec}초`;
  return `${sec}초`;
}

export function TimingHeader() {
  const [timing, setTiming] = useState<Timing | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const r = await fetch("/api/timing");
        const data = (await r.json()) as Timing;
        if (!cancelled) setTiming(data);
      } catch {
        /* be4fe 미기동 시 조용히 패스 */
      }
    }
    tick();
    const id = setInterval(tick, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <header className="timing-header">
      <span>
        <strong>시작:</strong>
        {timing?.started_at_iso ?? "—"}
      </span>
      <span>
        <strong>누적 경과:</strong>
        {formatElapsed(timing?.elapsed_seconds ?? null)}
      </span>
      <span>
        <strong>현재 시각:</strong>
        {timing?.now_iso ?? "—"}
      </span>
    </header>
  );
}
