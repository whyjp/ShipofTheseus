/**
 * Runtime 탭 — Q-D9 사전조건 + 게이트 7 부팅 검증 라이브 표기.
 *
 * runtime-prereq.md §부팅 검증 + boot_check.py 의 BootResult 라이브 표기.
 *
 * 5초 간격 /api/runtime 폴링. webview-builder 가 server.ts 에 다음 엔드포인트 추가:
 *   GET /api/runtime → {
 *     prereq: intent/04-runtime-prereq.md frontmatter,
 *     boot:   가장 최근 boot_check 결과 (BootResult JSON)
 *   }
 */
import { useEffect, useState } from "react";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

type Mode = "real" | "template" | "mock" | "none" | "pending";

type Prereq = {
  mode: Mode;
  env_satisfied: boolean | "pending";
  secrets_count: number;
  boot_command: string;
  healthz_url: string;
  env_hash?: string;        // sha256:... (mode=real 시, 평문 0)
  entry_blocked: boolean;
  qd9_answer?: 1 | 2 | 3 | 4 | null;
};

type BootResult = {
  boot_command: string;
  mode: string;
  healthz_url: string | null;
  boot_exit: number | string;     // int = exit code, str = "timeout" / "no-runtime" / ...
  healthz_status: number | string; // int = HTTP status, str = "skipped" / "error: ..."
  elapsed_s: number;
  pass_: boolean;
  ran_at?: string;
};

type RuntimePayload = {
  prereq: Prereq | null;
  boot: BootResult | null;
};

function ModeBadge({ mode }: { mode: Mode }) {
  const map: Record<Mode, { label: string; cls: string }> = {
    real:     { label: "실 모드 (real)",       cls: "good" },
    template: { label: "템플릿 (.env.template)", cls: "good" },
    mock:     { label: "Mock 부팅",             cls: "good" },
    none:     { label: "런타임 없음",           cls: "good" },
    pending:  { label: "대기 (Q-D9 미응답)",    cls: "bad" },
  };
  const m = map[mode] ?? { label: mode, cls: "bad" };
  return <span className={`score-pill ${m.cls}`}>{m.label}</span>;
}

function PassBadge({ pass_, label }: { pass_: boolean; label?: string }) {
  return (
    <span className={`score-pill ${pass_ ? "good" : "bad"}`}>
      {label ?? (pass_ ? "통과" : "미달")}
    </span>
  );
}

export function Runtime() {
  const [data, setData] = useState<RuntimePayload | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const r = await getJSON<RuntimePayload>("/api/runtime");
        if (!cancelled) {
          setData(r);
          setLoadError(null);
        }
      } catch (e) {
        if (!cancelled) setLoadError(String(e));
      }
    }
    tick();
    const id = setInterval(tick, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (loadError) {
    return (
      <EmptyState>
        /api/runtime 응답 실패 — webview-builder 가 server.ts 에 본 엔드포인트
        추가했는지 확인. ({loadError})
      </EmptyState>
    );
  }

  if (!data) {
    return <EmptyState>런타임 정보 로드 중…</EmptyState>;
  }

  const { prereq, boot } = data;

  if (!prereq) {
    return (
      <EmptyState>
        <p>아직 <code>intent/04-runtime-prereq.md</code> 가 없습니다.</p>
        <p>페이즈 04 의 Q-D9 답이 출하되면 본 탭이 자동 활성화됩니다.</p>
      </EmptyState>
    );
  }

  return (
    <div>
      <h2>
        Runtime 사전조건 + 게이트 7 <ModeBadge mode={prereq.mode} />
      </h2>

      {prereq.entry_blocked && (
        <p style={{ color: "var(--bad)", marginTop: 8 }}>
          ⚠️ <strong>entry_blocked</strong> — Q-D9 답이 미응답이거나 .env.template
          이 비었습니다. 페이즈 05 진입 거부 상태.
        </p>
      )}

      <h3 style={{ marginTop: 24 }}>사전조건 ({`Q-D9 답: ${prereq.qd9_answer ?? "—"}`})</h3>
      <table>
        <tbody>
          <tr><td><strong>mode</strong></td><td>{prereq.mode}</td></tr>
          <tr><td><strong>secrets_count</strong></td><td>{prereq.secrets_count}</td></tr>
          <tr>
            <td><strong>env_satisfied</strong></td>
            <td>
              {String(prereq.env_satisfied)}{" "}
              {prereq.env_satisfied === true && <PassBadge pass_={true} label="OK" />}
            </td>
          </tr>
          <tr>
            <td><strong>boot_command</strong></td>
            <td>{prereq.boot_command ? <code>{prereq.boot_command}</code> : "—"}</td>
          </tr>
          <tr>
            <td><strong>healthz_url</strong></td>
            <td>{prereq.healthz_url ? <code>{prereq.healthz_url}</code> : "—"}</td>
          </tr>
          {prereq.env_hash && (
            <tr>
              <td><strong>env_hash</strong></td>
              <td>
                <code style={{ fontSize: 12 }}>{prereq.env_hash}</code>{" "}
                <span style={{ color: "var(--fg-muted)", fontSize: 12 }}>
                  (sha256, 평문 0 — audit only)
                </span>
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <h3 style={{ marginTop: 24 }}>
        게이트 7 — 실 실행 1회 {boot && <PassBadge pass_={boot.pass_} />}
      </h3>
      {!boot ? (
        <p style={{ color: "var(--fg-muted)" }}>
          아직 boot_check 가 실행되지 않았습니다 (페이즈 09 진입 시 자동).
        </p>
      ) : (
        <table>
          <tbody>
            <tr><td><strong>boot_exit</strong></td><td><code>{String(boot.boot_exit)}</code></td></tr>
            <tr><td><strong>healthz_status</strong></td><td><code>{String(boot.healthz_status)}</code></td></tr>
            <tr><td><strong>elapsed</strong></td><td>{boot.elapsed_s.toFixed(2)} 초</td></tr>
            {boot.ran_at && <tr><td><strong>실행 시각</strong></td><td>{boot.ran_at}</td></tr>}
          </tbody>
        </table>
      )}

      <p style={{ marginTop: 24, color: "var(--fg-muted)", fontSize: 13 }}>
        본 탭은 5초 간격으로 /api/runtime 을 폴링합니다.
        runtime-prereq.md §부팅 검증 + boot_check.py 의 BootResult 라이브.
      </p>
    </div>
  );
}
