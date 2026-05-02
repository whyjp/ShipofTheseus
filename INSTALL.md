# 설치 가이드

## 한 줄 요약
**`git clone` 으로 받아 `.claude/skills/` 또는 `~/.claude/skills/` 에 심볼릭 링크 또는 복사한다.** 플러그인 매니페스트(`.claude-plugin/plugin.json`)는 향후 Claude Code 플러그인 매니저가 자동 인식할 수 있도록 미리 준비된 파일이다.

## 1. 프로젝트 단위 설치 (가장 권장)

특정 프로젝트에서만 본 스킬을 쓰고 싶을 때.

```bash
# 본 저장소를 적절한 위치에 클론
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus

# 본인 프로젝트 루트에서
cd /path/to/your/project
mkdir -p .claude/skills
ln -s ~/src/shipoftheseus/skills/theseus-harness .claude/skills/theseus-harness

# 또는 복사 (업스트림 갱신 추적이 필요 없을 때)
cp -r ~/src/shipoftheseus/skills/theseus-harness .claude/skills/
```

이후 Claude Code 세션에서:

```
/theseus-harness <요구사항>
```

## 2. 사용자 전역 설치

모든 프로젝트에서 호출하고 싶을 때.

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus
mkdir -p ~/.claude/skills
ln -s ~/src/shipoftheseus/skills/theseus-harness ~/.claude/skills/theseus-harness
```

## 3. Claude Code 플러그인 매니저 (향후)

본 저장소 루트의 `.claude-plugin/plugin.json` 은 Claude Code 의 플러그인 형식을 따른다. 플러그인 매니저가 지원되는 버전에서는:

```bash
claude plugin install https://github.com/whyjp/shipoftheseus
```

또는 마켓플레이스 등록 후 `claude plugin install shipoftheseus` 로 설치 가능 (해당 기능 가용성에 따라).

## 4. 업스트림 갱신

심볼릭 링크 설치라면:

```bash
cd ~/src/shipoftheseus
git pull origin main
# 별도 작업 불필요 — 링크가 항상 최신을 가리킨다
```

복사 설치라면 위 클론 위치에서 pull 후 다시 `cp -r`.

## 5. 의존성 (실행 시점)

본 스킬 자체는 외부 의존 없음. 단, 페이즈 12 가 생성하는 웹뷰는 다음을 요구:

ⓐ `bun` (1.x 이상) — 웹뷰 런타임. 미설치 시 https://bun.sh.
ⓑ Node.js 호환 환경 — `bun` 이 대부분 호환.

페이즈 10 의 테스트 매트릭스는 실행할 프로젝트의 스택에 의존:

ⓐ 백엔드 Go 기본값 → `go` 1.21+.
ⓑ 프론트엔드 → `bun`.
ⓒ E2E → Playwright (스킬이 자동 설치 안내).

## 6. 점검

설치 후:

```bash
# 스킬 디렉터리에서
python -m pytest skills/theseus-harness/scoring/test_score.py -q
```

11 테스트 모두 통과해야 정상 (DIP cap 2건 포함).

## 7. 제거

```bash
rm .claude/skills/theseus-harness          # 또는 ~/.claude/skills/theseus-harness
# 클론한 원본도 지우려면
rm -rf ~/src/shipoftheseus
```

## 트러블슈팅

ⓐ **`/theseus-harness` 슬래시 명령이 안 뜸** — `.claude/skills/theseus-harness/SKILL.md` 가 실제로 존재하는지 확인. 심볼릭 링크라면 깨지지 않았는지 `ls -L`.
ⓑ **웹뷰 `bun install` 실패** — bun 버전 확인 (`bun --version` ≥ 1.0). `package.json` 의존이 모두 설치되는지 확인.
ⓒ **Score 테스트 실패** — Python 3.10+ 필요 (PEP 604 union 문법 사용).
