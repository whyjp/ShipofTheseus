/**
 * Progress 탭 — state.json 라이브 폴링 + 진행 상태 추적.
 * resume.md §"FE 라이브 진행 추적" 의 구현.
 *
 * 5초 간격 /api/state 폴링. webview-builder 가 server.ts 에 다음 엔드포인트
 * 추가해야 함:
 *   GET /api/state  → .ShipofTheseus/<프로젝트>/state.json 그대로
 *   GET /api/resume → resume.py next 결과
 */
import { useEffect, useState } from "react";
import { getJSON } from "../lib/api";
import { EmptyState } from "../components/EmptyState";

type State = {
  project_id: string;
  status: "in_progress" | "interrupted" | "complete" | "user_paused";
  current_phase?: string | null;
  current_universe?: string | null;
  current_module?: string | null;
  current_sub_depth?: number;
  last_completed_phase?: string | null;
  last_completed_artifact?: string | null;
  active_skill?: string | null;
  active_agent?: string | null;
  pending_artifacts?: string[];
  completed_count?: number;
  total_estimated?: number;
  interrupt_reason?: string | null;
  resume_hint?: string | null;
  elapsed_seconds?: number;
};

type ResumePlan = {
  ok: boolean;
  action: string;
  entry_skill?: string;
  entry_input?: string;
  next_phase?: string;
  reason?: string;
  resume_command?: string;
};

function StatusBadge({ status }: { status: State["status"] }) {
  const map: Record<State["status"], { label: string; cls: string }> = {
    in_progress:  { label: "진행 중",  cls: "good" },
    interrupted:  { label: "중단됨",  cls: "bad" },
    complete:     { label: "완료",    cls: "good" },
    user_paused:  { label: "사용자 정지", cls: "bad" },
  };
  const m = map[status] ?? { label: status, cls: "bad" };
  return <span className={`score-pill ${m.cls}`}>{m.label}</span>;
}

export function Progress() {
  const [state, setState] = useState<State | null>(null);
  const [resumePlan, setResumePlan] = useState<ResumePlan | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      const s = await getJSON<State>("/api/state");
      if (!cancelled) setState(s);
      // 중단 상태일 때만 resume 계획 미리 가져옴
      if (s && (s.status === "interrupted" || s.status === "user_paused")) {
        const plan = await getJSON<ResumePlan>("/api/resume");
        if (!cancelled) setResumePlan(plan);
      }
    }
    tick();
    const id = setInterval(tick, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (!state) {
    return (
      <EmptyState>
        아직 state.json 이 없습니다 — 작업이 시작되지 않았거나 webview 가
        잘못된 프로젝트 디렉터리를 가리키고 있습니다.
      </EmptyState>
    );
  }

  const progress =
    state.completed_count != null && state.total_estimated
      ? Math.round((state.completed_count / state.total_estimated) * 100)
      : null;

  return (
    <div>
      <h2>
        진행 상태 <StatusBadge status={state.status} />
      </h2>

      <table style={{ marginTop: 12 }}>
        <tbody>
          <tr><td><strong>프로젝트</strong></td><td><code>{state.project_id}</code></td></tr>
          <tr><td><strong>현재 페이즈</strong></td><td>{state.current_phase ?? "—"}</td></tr>
          <tr><td><strong>활성 스킬</strong></td><td>{state.active_skill ?? "—"}</td></tr>
          <tr><td><strong>활성 에이전트</strong></td><td>{state.active_agent ?? "—"}</td></tr>
          <tr><td><strong>현재 우주</strong></td><td>{state.current_universe ?? "—"}</td></tr>
          <tr>
            <td><strong>현재 서브모듈</strong></td>
            <td>{state.current_module ? `${state.current_module} (depth ${state.current_sub_depth ?? 0})` : "—"}</td>
          </tr>
          <tr>
            <td><strong>마지막 완료</strong></td>
            <td>
              {state.last_completed_phase ?? "—"}
              {state.last_completed_artifact && (
                <> → <code>{state.last_completed_artifact}</code></>
              )}
            </td>
          </tr>
          {progress != null && (
            <tr>
              <td><strong>진행률</strong></td>
              <td>{state.completed_count} / {state.total_estimated} ({progress}%)</td>
            </tr>
          )}
          {state.elapsed_seconds != null && (
            <tr>
              <td><strong>누적 경과</strong></td>
              <td>{Math.floor(state.elapsed_seconds / 60)}분 {state.elapsed_seconds % 60}초</td>
            </tr>
          )}
        </tbody>
      </table>

      {state.pending_artifacts && state.pending_artifacts.length > 0 && (
        <>
          <h3 style={{ marginTop: 24 }}>대기 산출물</h3>
          <ul>
            {state.pending_artifacts.map((p, i) => <li key={i}><code>{p}</code></li>)}
          </ul>
        </>
      )}

      {(state.status === "interrupted" || state.status === "user_paused") && (
        <>
          <h3 style={{ marginTop: 24 }}>중단 사유</h3>
          <p>{state.interrupt_reason ?? "(미기록)"}</p>
          {resumePlan && (
            <>
              <h3>재개 권고</h3>
              <p>{resumePlan.reason}</p>
              {resumePlan.resume_command && (
                <pre><code>{resumePlan.resume_command}</code></pre>
              )}
              {resumePlan.action === "repair_required" && (
                <p style={{ color: "var(--bad)" }}>
                  ⚠️ 무결성 깨짐 — 자율 repair 시도 중 (handoff/13 에 사후 보고).
                </p>
              )}
            </>
          )}
        </>
      )}

      <p style={{ marginTop: 24, color: "var(--fg-muted)", fontSize: 13 }}>
        본 탭은 5초 간격으로 /api/state 를 폴링합니다. resume.md §"FE 라이브 진행 추적".
      </p>
    </div>
  );
}
