import { useState } from "react";
import { TimingHeader } from "./components/TimingHeader";
import { ModuleMap } from "./tabs/ModuleMap";
import { DesignIntent } from "./tabs/DesignIntent";
import { ImplIntent } from "./tabs/ImplIntent";
import { UnitTests } from "./tabs/UnitTests";
import { E2ETests } from "./tabs/E2ETests";
import { Sprints } from "./tabs/Sprints";

const TABS = [
  { id: "modules", label: "모듈 구성도", Component: ModuleMap },
  { id: "design", label: "설계 의도", Component: DesignIntent },
  { id: "impl", label: "구현 의도", Component: ImplIntent },
  { id: "unit", label: "단위 테스트", Component: UnitTests },
  { id: "e2e", label: "E2E 테스트", Component: E2ETests },
  { id: "sprints", label: "스프린트", Component: Sprints },
] as const;

export function App() {
  const [active, setActive] = useState<(typeof TABS)[number]["id"]>("modules");
  const Active = TABS.find((t) => t.id === active)!.Component;
  return (
    <div className="app">
      <TimingHeader />
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={t.id === active ? "active" : ""}
            onClick={() => setActive(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <main className="tab-body">
        <Active />
      </main>
    </div>
  );
}
