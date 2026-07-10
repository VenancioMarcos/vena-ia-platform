import {
  Bot,
  Boxes,
  BrainCircuit,
  CircleCheck,
  Factory,
  FileUp,
  Gauge,
  LayoutDashboard,
  MessageSquareText,
  ShieldCheck
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

const modules = [
  { name: "Projetos", status: "Planejado", icon: Boxes },
  { name: "Upload", status: "Planejado", icon: FileUp },
  { name: "Chat IA", status: "Base criada", icon: MessageSquareText },
  { name: "RAG", status: "Planejado", icon: BrainCircuit },
  { name: "CAD/CAM/CNC", status: "Roadmap", icon: Factory },
  { name: "Segurança", status: "Fundação", icon: ShieldCheck }
];

const milestones = [
  "Documentação oficial criada",
  "Arquitetura Modular Monolith aprovada",
  "Estrutura do monorepo iniciada",
  "API base com health check",
  "Frontend base operacional"
];

const navigationItems: Array<[string, LucideIcon]> = [
  ["Dashboard", LayoutDashboard],
  ["Projetos", Boxes],
  ["Arquivos", FileUp],
  ["Assistente", Bot],
  ["Indicadores", Gauge]
];

export default function Home() {
  return (
    <main className="min-h-screen bg-surface text-ink">
      <section className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded border border-line bg-ink text-white">
              <Gauge size={21} aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-semibold leading-5">Vena_IA Platform</p>
              <p className="text-xs text-steel">Engenharia inteligente para manufatura CNC</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 text-sm text-steel sm:flex">
            <CircleCheck size={17} className="text-signal" aria-hidden="true" />
            v0.1 Foundation
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[260px_1fr]">
        <aside className="border-r border-line pr-6">
          <nav className="grid gap-1">
            {navigationItems.map(([label, Icon]) => (
              <button
                key={label}
                className="flex h-10 items-center gap-3 rounded border border-transparent px-3 text-left text-sm text-machine hover:border-line hover:bg-white"
                type="button"
              >
                <Icon size={17} aria-hidden="true" />
                {label}
              </button>
            ))}
          </nav>
        </aside>

        <div className="grid gap-6">
          <header className="grid gap-3">
            <p className="text-sm font-medium text-signal">Console técnico</p>
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h1 className="text-3xl font-semibold tracking-normal text-ink">
                  Fundação operacional da Vena_IA
                </h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-steel">
                  Base inicial para projetos de engenharia, upload técnico, chat com IA, RAG e
                  evolução para CAD/CAM/CNC.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="border border-line bg-white px-4 py-3">
                  <p className="text-xs text-steel">Arquitetura</p>
                  <p className="font-semibold">Modular Monolith</p>
                </div>
                <div className="border border-line bg-white px-4 py-3">
                  <p className="text-xs text-steel">Roadmap</p>
                  <p className="font-semibold">v0.1</p>
                </div>
              </div>
            </div>
          </header>

          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {modules.map((module) => {
              const Icon = module.icon;
              return (
                <article key={module.name} className="border border-line bg-white p-4">
                  <div className="flex items-center justify-between">
                    <Icon size={20} className="text-machine" aria-hidden="true" />
                    <span className="text-xs font-medium text-signal">{module.status}</span>
                  </div>
                  <h2 className="mt-4 text-base font-semibold">{module.name}</h2>
                </article>
              );
            })}
          </section>

          <section className="grid gap-4 lg:grid-cols-[1fr_320px]">
            <div className="border border-line bg-white p-5">
              <h2 className="text-base font-semibold">Marcos da fundação</h2>
              <div className="mt-4 grid gap-3">
                {milestones.map((item) => (
                  <div key={item} className="flex items-center gap-3 text-sm text-machine">
                    <CircleCheck size={17} className="text-signal" aria-hidden="true" />
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="border border-line bg-white p-5">
              <h2 className="text-base font-semibold">Próximo bloco</h2>
              <div className="mt-4 grid gap-3 text-sm leading-6 text-steel">
                <p>Banco inicial, migrations, autenticação e persistência dos projetos.</p>
                <p className="font-medium text-ink">Fase 3-7</p>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
