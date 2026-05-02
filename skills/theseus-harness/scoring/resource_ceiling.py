#!/usr/bin/env python3
"""
리소스 천정 감지 + 자동 임계 조정 권고.

resources.md 의 알고리즘을 코드로 구현. 측정 시계열과 추정 천정을 받아
"이 리소스에서 더 못 짠다" 신호와 권고 임계를 산출.

사용:
    resource_ceiling.py --measurements meas.json [--window 3] [--ceiling-pct 0.90]

입력 JSON:
    {
      "measurements": [340, 342, 341],         # 직전 N 측정값 (ms 또는 RPS)
      "current_threshold": 200,                 # 현재 임계 (ms 면 < 비교, RPS 면 > 비교)
      "estimated_ceiling": 350,                 # resources.md 의 추정 천정
      "metric": "p99_ms"                        # p99_ms | rps | latency_ms — 비교 방향 결정
    }

stdout JSON, exit 0 = 천정 아님, 1 = 천정 도달 (자동 조정 권고).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


LATENCY_METRICS = {"p99_ms", "p95_ms", "p50_ms", "latency_ms"}
THROUGHPUT_METRICS = {"rps", "qps", "throughput"}


def detect(
    measurements: list[float],
    current_threshold: float,
    estimated_ceiling: float,
    metric: str = "p99_ms",
    window: int = 3,
    ceiling_pct: float = 0.90,
    spread_eps: float = 0.05,
    safety_margin: float = 0.05,
) -> dict:
    """
    천정 도달 신호:
      - 직전 N 측정값이 추정 천정의 ceiling_pct 이상 (latency: avg ≥ ceiling*pct,
        throughput: avg ≤ ceiling*(2-pct) — 즉 천정에 가까이)
      - 측정값 spread 가 spread_eps 이내 (안정됨)
      - 임계 미달 (조정 검토 가치)
    권고 임계:
      - latency: 안정 측정값 × (1 + safety_margin)
      - throughput: 안정 측정값 × (1 - safety_margin)
    """
    if metric not in LATENCY_METRICS | THROUGHPUT_METRICS:
        return {"near_ceiling": False, "error": f"unsupported metric: {metric}"}

    if len(measurements) < window:
        return {"near_ceiling": False, "reason": "측정값 부족 (window 미달)"}

    recent = measurements[-window:]
    avg = sum(recent) / window
    spread = max(recent) - min(recent)
    rel_spread = spread / avg if avg else 0.0

    is_latency = metric in LATENCY_METRICS

    # 안정성 체크
    if rel_spread >= spread_eps:
        return {
            "near_ceiling": False,
            "avg": avg,
            "spread": spread,
            "rel_spread": round(rel_spread, 4),
            "reason": "측정값 변동 큼 (spread > eps) — 천정 판단 보류",
        }

    # 임계 미달 검사
    fails_threshold = (avg > current_threshold) if is_latency else (avg < current_threshold)
    if not fails_threshold:
        return {
            "near_ceiling": False,
            "avg": avg,
            "reason": "현재 임계 충족 — 조정 불필요",
        }

    # 천정 근접
    pct_actual = (
        avg / estimated_ceiling
        if is_latency
        else avg / estimated_ceiling
    )
    near = (avg >= estimated_ceiling * ceiling_pct) if is_latency else (avg <= estimated_ceiling * (2 - ceiling_pct) and avg >= estimated_ceiling * ceiling_pct)
    # latency: 천정에 *가까운* 큰 값 (avg ≥ 0.9 × ceiling)
    # throughput: 천정에 *가까운* 작은 값 — 같은 식, RPS 추정 천정의 0.9 이상이면 근접
    near = avg >= estimated_ceiling * ceiling_pct if is_latency else avg >= estimated_ceiling * ceiling_pct

    if not near:
        return {
            "near_ceiling": False,
            "avg": avg,
            "ceiling_pct_actual": round(pct_actual, 3),
            "reason": (
                f"측정 평균 {avg:.2f} 이 추정 천정 {estimated_ceiling} 의 "
                f"{pct_actual*100:.1f}% — 더 개선 여지 있음 (rewrite 권고)"
            ),
        }

    # 권고 임계
    if is_latency:
        recommended = round(avg * (1 + safety_margin), 2)
    else:
        recommended = round(avg * (1 - safety_margin), 2)

    return {
        "near_ceiling": True,
        "avg": round(avg, 2),
        "spread": round(spread, 4),
        "rel_spread": round(rel_spread, 4),
        "ceiling_pct_actual": round(pct_actual, 3),
        "current_threshold": current_threshold,
        "recommended_threshold": recommended,
        "metric": metric,
        "is_latency": is_latency,
        "reason": (
            f"{window} 스프린트 평균 {avg:.2f} 이 추정 천정 {estimated_ceiling} 의 "
            f"{pct_actual*100:.1f}% — 변동 안정 ({rel_spread*100:.1f}%) → 개선 불가능 신호. "
            f"임계 → {recommended} ({'안전 여유' if is_latency else '하향 여유'} {safety_margin*100:.0f}%). "
            f"autonomy.md 의 Q-D3 사전 위임 답에 매핑해 자율 적용 (인터뷰 후 인터럽트 0)."
        ),
        # 사전 위임 정책 매핑 (autonomy.md Q-D3) — 인터뷰 후 ack 호출 없음
        "policy_actions": {
            "1": {"action": "set_threshold", "value": recommended,
                  "desc": "권고 임계로 자동 조정 (default)"},
            "2": {"action": "upgrade_resource", "value": "next_tier",
                  "desc": "리소스 프로파일 한 단계 상향 (비용 사전 동의 시)"},
            "3": {"action": "domain_simplify", "value": None,
                  "desc": "도메인 단순화 자동 시도 (캐시/인덱스/비동기)"},
            "4": {"action": "accept_stagnation", "value": None,
                  "desc": "정체 수용 — 해당 차원 게이트 비활성"},
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--measurements", required=True, help="meas.json 경로")
    p.add_argument("--window", type=int, default=3)
    p.add_argument("--ceiling-pct", type=float, default=0.90)
    p.add_argument("--spread-eps", type=float, default=0.05)
    p.add_argument("--safety-margin", type=float, default=0.05)
    args = p.parse_args(argv)

    data = json.loads(Path(args.measurements).read_text(encoding="utf-8"))
    out = detect(
        measurements=data["measurements"],
        current_threshold=data["current_threshold"],
        estimated_ceiling=data["estimated_ceiling"],
        metric=data.get("metric", "p99_ms"),
        window=args.window,
        ceiling_pct=args.ceiling_pct,
        spread_eps=args.spread_eps,
        safety_margin=args.safety_margin,
    )
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if out.get("near_ceiling") else 0


if __name__ == "__main__":
    sys.exit(main())
