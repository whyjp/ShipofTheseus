# 설치 가이드

## 한 줄 요약

**`git clone` 으로 받아 `.claude/skills/` 또는 `~/.claude/skills/` 에 9 스킬을 일괄 링크 (또는 복사) 한다.** 플러그인 매니페스트(`.claude-plugin/plugin.json`)는 Claude Code 플러그인 매니저가 9 스킬을 한 번에 등록할 수 있도록 준비된 파일이다.

## 어떤 스킬이 설치되는가

본 저장소는 9 스킬을 묶음으로 배포한다 — 1 인덱스 + 7 페이즈 분해 + 1 플래그십(단일 source of truth):

```
skills/
├── theseus-orchestrator/   # 14 페이즈를 7 분해 스킬로 위임하는 인덱스
├── theseus-intent/         # 페이즈 00–05 (명명·의도·인터뷰·비평)
├── theseus-plan/           # 페이즈 06–07 (TODO DAG·재이해)
├── theseus-implement/      # 페이즈 08 (모듈 단위 구현)
├── theseus-quality/        # 페이즈 09 (5 게이트)
├── theseus-sprint/         # 페이즈 10–11 (무한 루프·바이섹트·멀티버스)
├── theseus-webview/        # 페이즈 12 (bun 웹뷰)
├── theseus-handoff/        # 페이즈 13 (요약·PR)
└── theseus-harness/        # 플래그십 — 21 컨벤션 + 14 페이즈 + 13 에이전트 + 채점기
```

스킬 간 인터페이스는 산출물 frontmatter ([`skills/theseus-harness/conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md))가 계약 — 검증 실패 시 다음 스킬이 진입을 거부.

## 1. 프로젝트 단위 설치 (가장 권장)

특정 프로젝트에서만 본 묶음을 쓰고 싶을 때.

```bash
# 본 저장소를 적절한 위치에 클론
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus

# 본인 프로젝트 루트에서 — 9 스킬 일괄 링크
cd /path/to/your/project
mkdir -p .claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" ".claude/skills/$(basename "$s")"
done

# 또는 일괄 복사 (업스트림 갱신 추적이 필요 없을 때)
cp -r ~/src/shipoftheseus/skills/* .claude/skills/
```

이후 Claude Code 세션에서:

```
/theseus-orchestrator <요구사항>   # 14 페이즈 자동 진행 (권장)
/theseus-harness <요구사항>        # 단일 source of truth 직접 호출
/theseus-plan <요구사항>           # 외부 intent 산출물로 plan 부터 재진입
```

### 일부만 설치

플래그십만 쓰는 경우(단일 호출):

```bash
ln -s ~/src/shipoftheseus/skills/theseus-harness .claude/skills/theseus-harness
```

orchestrator + 분해 7 개만(플래그십 단일 source of truth 는 같이 설치 권장 — 분해 스킬이 본문을 위임하기 때문):

```bash
for s in theseus-orchestrator theseus-intent theseus-plan theseus-implement \
         theseus-quality theseus-sprint theseus-webview theseus-handoff \
         theseus-harness; do
  ln -s "$HOME/src/shipoftheseus/skills/$s" ".claude/skills/$s"
done
```

> **주의** — 분해 스킬(`theseus-intent`/`theseus-plan` 등)은 콘텐츠를 `theseus-harness/` 경로로 위임한다. 분해 스킬만 설치하고 플래그십을 빠뜨리면 페이즈 본문 링크가 깨진다.

## 2. 사용자 전역 설치

모든 프로젝트에서 호출하고 싶을 때.

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus
mkdir -p ~/.claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" "$HOME/.claude/skills/$(basename "$s")"
done
```

## 3. Claude Code 플러그인 매니저 (권장 미래 형태)

본 저장소 루트의 `.claude-plugin/plugin.json` 은 9 스킬 모두를 선언한다. 플러그인 매니저가 지원되는 버전에서는:

```bash
claude plugin install https://github.com/whyjp/shipoftheseus
```

또는 마켓플레이스 등록 후 `claude plugin install shipoftheseus` 로 설치 가능 (해당 기능 가용성에 따라). 9 스킬이 한 번에 등록된다.

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
# 일괄 점검 — 35 self_lint 체크 + pytest + sample 채점 + 자기 점수 + 핑거프린트 체인
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

자기 점수 임계 0.99999 통과 + self_lint 35/35 + pytest 모두 통과해야 정상.

## 7. 제거

```bash
# 9 스킬 일괄 제거
rm .claude/skills/theseus-*       # 또는 ~/.claude/skills/theseus-*

# 클론한 원본도 지우려면
rm -rf ~/src/shipoftheseus
```

## 트러블슈팅

ⓐ **`/theseus-*` 슬래시 명령이 안 뜸** — `.claude/skills/<스킬명>/SKILL.md` 가 실제로 존재하는지 확인. 심볼릭 링크라면 깨지지 않았는지 `ls -L .claude/skills/`. Claude Code 재시작 필요.
ⓑ **분해 스킬에서 페이즈 본문 링크가 깨짐** — `theseus-harness` 도 같이 설치되어 있는지 확인. 분해 스킬은 단일 source of truth 를 `../theseus-harness/` 상대 경로로 참조한다.
ⓒ **웹뷰 `bun install` 실패** — bun 버전 확인 (`bun --version` ≥ 1.0). `package.json` 의존이 모두 설치되는지 확인.
ⓓ **Score 테스트 실패** — Python 3.10+ 필요. `python --version` 확인.
ⓔ **frontmatter 검증 실패로 페이즈 진입 거부** — 외부에서 받은 산출물이라면 [`skills/theseus-harness/scoring/fingerprint.py`](skills/theseus-harness/scoring/fingerprint.py) 의 `verify` 와 `chain` 명령으로 무결성을 먼저 점검:

```bash
python skills/theseus-harness/scoring/fingerprint.py verify --file <산출물>
python skills/theseus-harness/scoring/fingerprint.py chain --dir .ShipofTheseus/<프로젝트>/
```
