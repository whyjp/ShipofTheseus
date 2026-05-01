/**
 * be4fe — Hono 기반 백엔드-포-프론트엔드.
 * `.ShipofTheseus/<프로젝트>/` 산출물을 읽어 fe 가 소비할 JSON 으로 노출한다.
 *
 * 실행: bun --hot server.ts
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { streamSSE } from "hono/streaming";
import { readdir, readFile, stat, watch } from "node:fs/promises";
import { existsSync, watch as fsWatch } from "node:fs";
import { join, relative } from "node:path";

const ROOT = process.env.THESEUS_ROOT ?? join(process.cwd(), "..");
// webview 는 .ShipofTheseus/<project>/webview 안에 있으므로 부모가 프로젝트 루트
const PROJECT_ROOT = ROOT;

const app = new Hono();
app.use("*", cors());

const startedAt = await readJsonOptional(join(PROJECT_ROOT, "timing/start.json"));

app.get("/api/timing", async (c) => {
  const now = Date.now();
  const startedAtUnix = startedAt?.started_at_unix ?? null;
  return c.json({
    started_at_iso: startedAt?.started_at_iso ?? null,
    started_at_unix: startedAtUnix,
    now_iso: new Date(now).toISOString(),
    now_unix: Math.floor(now / 1000),
    elapsed_seconds: startedAtUnix ? Math.floor(now / 1000) - startedAtUnix : null,
  });
});

app.get("/api/intent", async (c) => {
  const dir = join(PROJECT_ROOT, "intent");
  return c.json(await collectMarkdown(dir));
});

app.get("/api/plan", async (c) => {
  const dir = join(PROJECT_ROOT, "plan");
  return c.json(await collectMarkdown(dir));
});

app.get("/api/impl", async (c) => {
  return c.json({
    impl: await readMarkdownOptional(join(PROJECT_ROOT, "impl/08-impl-log.md")),
    quality: await readMarkdownOptional(
      join(PROJECT_ROOT, "quality/09-quality-gate.md"),
    ),
  });
});

app.get("/api/naming", async (c) => {
  return c.json(await collectMarkdown(join(PROJECT_ROOT, "naming")));
});

app.get("/api/sprints", async (c) => {
  const dir = join(PROJECT_ROOT, "sprints");
  if (!existsSync(dir)) return c.json([]);
  const sprints: any[] = [];
  for (const name of (await readdir(dir)).sort()) {
    const sdir = join(dir, name);
    if (!(await stat(sdir)).isDirectory()) continue;
    sprints.push({
      sprint: name,
      report: await readMarkdownOptional(join(sdir, "report.md")),
      inputs: await readJsonOptional(join(sdir, "inputs.json")),
      bisect: await readMarkdownOptional(join(sdir, "bisect.md")),
    });
  }
  return c.json(sprints);
});

app.get("/api/tests/unit", async (c) => {
  // Go go test -json 또는 bun test --reporter=json 결과를 정규화 (구현은 프로젝트별).
  const path = join(PROJECT_ROOT, "sprints");
  if (!existsSync(path)) return c.json({ sprints: [] });
  const sprints = (await readdir(path)).sort();
  const out: any[] = [];
  for (const s of sprints) {
    const unitJson = join(path, s, "unit.json");
    if (existsSync(unitJson)) {
      out.push({ sprint: s, results: await readJsonOptional(unitJson) });
    }
  }
  return c.json({ sprints: out });
});

app.get("/api/tests/e2e", async (c) => {
  const path = join(PROJECT_ROOT, "sprints");
  if (!existsSync(path)) return c.json({ sprints: [] });
  const sprints = (await readdir(path)).sort();
  const out: any[] = [];
  for (const s of sprints) {
    const e2eJson = join(path, s, "e2e.json");
    if (existsSync(e2eJson)) {
      out.push({ sprint: s, results: await readJsonOptional(e2eJson) });
    }
  }
  return c.json({ sprints: out });
});

app.get("/api/events", (c) => {
  // 파일 변경 감시 → SSE 푸시. 클라이언트는 EventSource 로 구독.
  return streamSSE(c, async (stream) => {
    const watcher = fsWatch(PROJECT_ROOT, { recursive: true }, async (event, filename) => {
      if (!filename) return;
      await stream.writeSSE({
        event: "change",
        data: JSON.stringify({ event, path: filename, at: new Date().toISOString() }),
      });
    });
    stream.onAbort(() => watcher.close());
    while (true) {
      // keep-alive
      await stream.writeSSE({ event: "ping", data: String(Date.now()) });
      await new Promise((r) => setTimeout(r, 15000));
    }
  });
});

// ─── helpers ──────────────────────────────────────────────────────────────

async function readJsonOptional(path: string): Promise<any | null> {
  if (!existsSync(path)) return null;
  return JSON.parse(await readFile(path, "utf8"));
}

async function readMarkdownOptional(path: string): Promise<string | null> {
  if (!existsSync(path)) return null;
  return await readFile(path, "utf8");
}

async function collectMarkdown(dir: string): Promise<Record<string, string>> {
  if (!existsSync(dir)) return {};
  const out: Record<string, string> = {};
  for (const name of (await readdir(dir)).sort()) {
    if (!name.endsWith(".md")) continue;
    out[name] = await readFile(join(dir, name), "utf8");
  }
  return out;
}

const port = Number(process.env.PORT ?? 5174);
console.log(`be4fe 서버 기동: http://localhost:${port}  (PROJECT_ROOT=${PROJECT_ROOT})`);
export default { port, fetch: app.fetch };
