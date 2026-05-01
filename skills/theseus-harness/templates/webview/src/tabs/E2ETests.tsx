import { useEffect, useState } from "react";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

type E2EData = { sprints: { sprint: string; results: any }[] };

export function E2ETests() {
  const [data, setData] = useState<E2EData | null>(null);
  const [openSprint, setOpenSprint] = useState<string | null>(null);
  const [openCase, setOpenCase] = useState<string | null>(null);
  useEffect(() => {
    getJSON<E2EData>("/api/tests/e2e").then(setData);
  }, []);

  if (!data || data.sprints.length === 0) {
    return <EmptyState>아직 E2E 결과가 없습니다. 테스터 에이전트가 sprints/NN/e2e.json 을 생성하면 시나리오·스크린샷·스텝이 여기에 인터랙티브로 표시됩니다.</EmptyState>;
  }

  return (
    <div>
      {data.sprints.map((s) => {
        const r = s.results ?? {};
        const cases = r.cases ?? [];
        return (
          <div className="sprint-row" key={s.sprint}>
            <h3
              style={{ cursor: "pointer" }}
              onClick={() => setOpenSprint(openSprint === s.sprint ? null : s.sprint)}
            >
              스프린트 {s.sprint} — {cases.length} 시나리오
            </h3>
            {openSprint === s.sprint && (
              <ul>
                {cases.map((c: any) => {
                  const id = `${s.sprint}/${c.name}`;
                  return (
                    <li key={c.name}>
                      <span
                        style={{ cursor: "pointer" }}
                        onClick={() => setOpenCase(openCase === id ? null : id)}
                      >
                        <span className={`score-pill ${c.status === "passed" ? "good" : "bad"}`}>
                          {c.status}
                        </span>
                        {" "}
                        <code>{c.name}</code>
                      </span>
                      {openCase === id && (
                        <ol>
                          {(c.steps ?? []).map((step: any, i: number) => (
                            <li key={i}>
                              {step.title} <small>({step.duration ?? "—"})</small>
                              {step.error && <pre>{step.error}</pre>}
                              {step.screenshot && (
                                <img src={step.screenshot} alt="" style={{ maxWidth: "100%" }} />
                              )}
                            </li>
                          ))}
                        </ol>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}
