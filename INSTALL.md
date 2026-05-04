# 설치 가이드

## 한 줄 요약

**`git clone` 으로 받아 `.claude/skills/` 또는 `~/.claude/skills/` 에 2 스킬을 일괄 링크 (또는 복사) 한다.** 플러그인 매니페스트(`.claude-plugin/plugin.json`)는 Claude Code 플러그인 매니저가 2 스킬을 한 번에 등록할 수 있도록 준비된 파일이다.

## 어떤 스킬이 설치되는가

본 저장소는 v0.9.15 기준 2 스킬을 묶음으로 배포한다 — 1 entry + 1 source of truth:

```
skills/
├── theseus-orchestrator/   # 사용자 entry — HARD-RULE + 그레이드 인덱스 (theseus-harness 동반 필수)
└── theseus-harness/        # 콘텐츠 source — 47 컨벤션 + 15 페이즈 + 18 에이전트 + 2 도메인 어댑터 + scoring/ + templates/
```

> **v0.9.0 sprint-03-b 단순화** — 이전 9 SKILL.md (orchestrator + 7 phase 분해 stub + harness) 에서 7 phase stub 제거. pure delegation 이라 cost > benefit 으로 판정 (livetest #1 fail 분석). 사용자 entry namespace `/shipoftheseus:theseus-orchestrator` 동일.

페이즈 산출물 frontmatter ([`skills/theseus-harness/conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md)) 가 계약 — fingerprint chain 으로 다음 페이즈 진입 검증.

## Fresh User 환경 점검 (v0.4.0 — ralph bootstrap 거울)

본 하네스를 처음 사용하는 환경은 페이즈별 다른 도구가 필요하다 — Phase 08 (구현) 은 Go + bun, Phase 12 (웹뷰) 는 bun + node, Phase 09/10 (게이트/스프린트) 은 Python 3 + pytest. 사용자가 호출 직후 페이즈 04 (스택 점검) 에서 자동 진단되지만, *호출 전* 에 fresh-user 환경이 정합한지 빠르게 자가 점검하려면:

```bash
# Linux/Mac
bash scripts/self-check.sh --check-stack-only

# Windows
scripts\self-check.bat --check-stack-only
```

위 명령은 다음을 출력:

```
[stack-check] python3: ✓ (3.11.5)
[stack-check] go:      ✓ (1.21.0)
[stack-check] bun:     ✗ — install via 'curl -fsSL https://bun.sh/install | bash'
[stack-check] node:    ✓ (20.10.0)
[stack-check] pytest:  ✓ (7.4.0)
```

`✗` 항목은 호출 직전 직접 설치 권장. 그렇지 않으면 페이즈 04 의 [`conventions/stack.md`](skills/theseus-harness/conventions/stack.md) Q-D5 답에 따라 자율 업데이트 (`asdf/nvm/goenv` 안에서) 시도. **본 절은 ralph 의 `.ralph/bootstrap.sh` 의 직교 차원 차용** — *기존 stack.md + Q-D5 의 정책 답안* + *실행 직전 진단* 추가 (거울 원칙: 새 파일 X, 기존 한 절 증강).

## 1. 프로젝트 단위 설치 (가장 권장)

특정 프로젝트에서만 본 묶음을 쓰고 싶을 때.

```bash
# 본 저장소를 적절한 위치에 클론
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus

# 본인 프로젝트 루트에서 — 2 스킬 (orchestrator + harness) 모두 링크
cd /path/to/your/project
mkdir -p .claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" ".claude/skills/$(basename "$s")"
done
```

이후 Claude Code 세션에서:

```
/shipoftheseus:theseus-orchestrator <요구사항>   # 15 페이즈 자율 driver (사용자 entry)
```

> **두 스킬 모두 설치 필수** — `theseus-orchestrator` 는 HARD-RULE entry 룰 + 그레이드 인덱스만 정의. 콘텐츠 source 는 `theseus-harness/` 가 가짐. 한 쪽만 설치하면 동작 안 함.

## 2. 사용자 전역 설치

모든 프로젝트에서 호출하고 싶을 때.

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus
mkdir -p ~/.claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" "$HOME/.claude/skills/$(basename "$s")"
done
```

## 3. Claude Code 플러그인 매니저 — 마켓플레이스 패턴 (권장)

본 저장소는 *동시에* 마켓플레이스 + 단일 플러그인 역할 — `.claude-plugin/marketplace.json` 이 본 repo 를 마켓플레이스로 등록하고 `.claude-plugin/plugin.json` 이 2 스킬을 선언. Claude Code 세션 안에서:

```bash
# ① 마켓플레이스 등록 (한 번만)
/plugin marketplace add https://github.com/whyjp/shipoftheseus

# ② 플러그인 설치
/plugin install shipoftheseus@shipoftheseus
```

설치 후 2 스킬 (`/shipoftheseus:theseus-orchestrator`, `/shipoftheseus:theseus-harness`) 이 한 번에 등록된다. 업데이트는 `/plugin marketplace update shipoftheseus` 로 원격 변경 반영.

> **⚠️ `claude plugin install <url>` 직접 호출은 안 됨** — Claude Code 의 플러그인 매니저는 마켓플레이스에 *먼저 등록된* 플러그인만 설치한다. URL 직접 install 패턴은 미지원이며 `Plugin not found in any configured marketplace` 에러가 난다. 위 두 단계가 표준.

## 4. 업스트림 갱신

심볼릭 링크 설치라면:

```bash
cd ~/src/shipoftheseus
git pull origin main
# 별도 작업 불필요 — 링크가 항상 최신을 가리킨다
```

복사 설치라면 위 클론 위치에서 pull 후 다시 일괄 복사:

```bash
cp -r ~/src/shipoftheseus/skills/* /path/to/your/project/.claude/skills/
```

## 5. 의존성 (실행 시점)

본 스킬 자체는 외부 의존 없음. 단, 실행 환경에 따라 다음을 요구:

ⓐ **자기 평가 / 채점** — Python 3.10+ (PEP 604 union 문법 사용). `pytest` 권장.
ⓑ **페이즈 12 웹뷰** — `bun` 1.x 이상. 미설치 시 https://bun.sh.
ⓒ **페이즈 10 테스트 매트릭스** — 실행할 프로젝트의 스택에 의존:
  - 백엔드 Go 기본값 → `go` 1.21+.
  - 프론트엔드 → `bun`.
  - E2E → Playwright (스킬이 자동 설치 안내).

## 6. 점검

설치 후 (저장소 루트에서):

```bash
# 일괄 점검 — self_lint 60+ 체크 + pytest + sample 채점 + 자기 점수 + 핑거프린트 체인
./scripts/self-check.sh        # linux/mac
scripts\self-check.bat         # windows
```

또는 개별:

```bash
python skills/theseus-harness/scoring/self_lint.py
python -m pytest skills/theseus-harness/scoring/ -q
python skills/theseus-harness/scoring/score.py \
  --inputs skills/theseus-harness/templates/sample-inputs.json
```

자기 점수 임계 0.99999 통과 + self_lint 모든 룰 PASS + pytest 모두 통과해야 정상.

## 7. 제거

```bash
# 2 스킬 일괄 제거
rm .claude/skills/theseus-*       # 또는 ~/.claude/skills/theseus-*

# 클론한 원본도 지우려면
rm -rf ~/src/shipoftheseus
```

## 트러블슈팅

ⓐ **`/theseus-*` 슬래시 명령이 안 뜸** — `.claude/skills/<스킬명>/SKILL.md` 가 실제로 존재하는지 확인. 심볼릭 링크라면 깨지지 않았는지 `ls -L .claude/skills/`. Claude Code 재시작 필요.
ⓑ **`theseus-orchestrator` 만 설치 시 본문 링크가 깨짐** — `theseus-harness` 도 같이 설치되어 있는지 확인. orchestrator 의 룰 본문은 `../theseus-harness/` 상대 경로로 참조한다 (HARD-RULE + 그레이드 인덱스만 자체 보유).
ⓒ **웹뷰 `bun install` 실패** — bun 버전 확인 (`bun --version` ≥ 1.0). `package.json` 의존이 모두 설치되는지 확인.
ⓓ **Score 테스트 실패** — Python 3.10+ 필요. `python --version` 확인.
ⓔ **frontmatter 검증 실패로 페이즈 진입 거부** — 외부에서 받은 산출물이라면 [`skills/theseus-harness/scoring/fingerprint.py`](skills/theseus-harness/scoring/fingerprint.py) 의 `verify` 와 `chain` 명령으로 무결성을 먼저 점검:

```bash
python skills/theseus-harness/scoring/fingerprint.py verify --file <산출물>
python skills/theseus-harness/scoring/fingerprint.py chain --dir .ShipofTheseus/<프로젝트>/
```
