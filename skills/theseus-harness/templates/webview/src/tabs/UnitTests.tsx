import { useEffect, useState } from "react";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

type UnitData = { sprints: { sprint: string; results: any }[] };

export function UnitTests() {
  const [data, setData] = useState<UnitData | null>(null);
  const [openSprint, setOpenSprint] = useState<string | null>(null);
  useEffect(() => {
    getJSON<UnitData>("/api/tests/unit").then(setData);
  }, []);

  if (!data || data.sprints.length === 0) {
    return <EmptyState>아직 단위 테스트 결과가 없습니다. 테스터 에이전트가 sprints/NN/unit.json 을 생성하면 여기에 표시됩니다.</EmptyState>;
  }

  return (
    <div>
      {data.sprints.map((s) => {
        const r = s.results ?? {};
        const total = r.total ?? 0;
        const failed = r.failed ?? 0;
        return (
          <div className="sprint-row" key={s.sprint}>
            <h3
              style={{ cursor: "pointer" }}
              onClick={() => setOpenSprint(openSprint === s.sprint ? null : s.sprint)}
            >
              스프린트 {s.sprint}
              <span
                className={`score-pill ${failed === 0 ? "good" : "bad"}`}
                style={{ marginLeft: 12 }}
              >
                {total - failed} / {total} 통과
              </span>
            </h3>
            {openSprint === s.sprint && (
              <ul>
                {(r.failures ?? []).map((f: any, i: number) => (
                  <li key={i}>
                    <code>{f.path}::{f.name}</code> — {f.message}
                  </li>
                ))}
                {(r.failures ?? []).length === 0 && <li>실패 없음</li>}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}
