#!/usr/bin/env python3
"""_stdio.py — scoring 파이프라인 CLI 진입점 공유 유틸: stdout/stderr UTF-8 강제.

WHY: cp949 등 로캘 콘솔에서 리포트에 든 비-ASCII(em-dash '—' U+2014 / 한글)를
`print`·`json.dump(..., sys.stdout)` 하면 기본 인코딩이 OS 로케일이라
`UnicodeEncodeError` 로 크래시(exit 1)한다. 저장소 self_lint C35(파일 IO utf-8 명시)
원칙을 stdout/stderr 까지 확장하는 단일 지점이다 — 같은 reconfigure 스니펫을 각 CLI 에
복제하면 이 저장소의 DRY 체커가 감시하는 위반이므로 여기 한 번만 정의하고 각 `main()`
이 재사용한다(§2 원칙4 "줄인다").

이 모듈은 출력 스트림 인코딩만 손댄다 — 어떤 verdict/measured/판정 값도 만들거나
바꾸지 않는다.
"""
from __future__ import annotations

import sys


def force_utf8_stdio() -> None:
    """stdout/stderr 를 UTF-8 로 재설정 — cp949 등 로캘 콘솔에서 비-ASCII(—/한글)
    print 크래시 방지. pytest capture 등 reconfigure 불가 스트림은 조용히 건너뛴다."""
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8")  # py3.7+ TextIOWrapper
        except (AttributeError, ValueError):
            pass
