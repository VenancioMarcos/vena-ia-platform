import { TurningViewerContainer } from "../../../components/cam/TurningViewerContainer";

export default function TurningInspectorPage() {
  return <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:px-8">
    <div className="mx-auto w-full max-w-4xl space-y-6">
      <header className="space-y-3">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">CAM Turning 2D Profile Inspector (Synthetic Sandbox)</h1>
        <p className="rounded-lg border border-slate-700 bg-slate-900 p-4 text-sm text-slate-200">
          Ambiente de inspeção geométrica sintética 2D. Operações de usinagem física desautorizadas.
        </p>
      </header>
      <TurningViewerContainer />
    </div>
  </main>;
}
