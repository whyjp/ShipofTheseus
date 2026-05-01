/**
 * be4fe API 의 fetch 래퍼 + 빈 상태 안내 헬퍼.
 * 6 탭 모두 항상 렌더 — 데이터 없으면 EmptyState 컴포넌트로 안내.
 */

export async function getJSON<T>(path: string): Promise<T | null> {
  try {
    const r = await fetch(path);
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}
