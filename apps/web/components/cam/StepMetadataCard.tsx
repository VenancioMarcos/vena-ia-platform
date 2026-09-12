import type { StepGeometryInspection } from "../../lib/step-geometry-adapter";

type Props = Readonly<{ inspection: StepGeometryInspection }>;

/** Read-only client inspection summary. It never enables geometry dispatch or emission. */
export function StepMetadataCard({ inspection }: Props) {
  const { metadata } = inspection;
  return <details className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm">
    <summary className="cursor-pointer font-medium">Metadados da inspeção STEP local</summary>
    <dl className="mt-2 grid gap-1 text-slate-200">
      <div><dt className="inline text-slate-400">Schema: </dt><dd className="inline">{metadata.schema}</dd></div>
      <div><dt className="inline text-slate-400">Unidade: </dt><dd className="inline">{metadata.lengthUnit}</dd></div>
      <div><dt className="inline text-slate-400">Bytes lidos: </dt><dd className="inline">{metadata.bytesRead}</dd></div>
      <div><dt className="inline text-slate-400">B-Rep sólida: </dt><dd className="inline">{inspection.supported ? "Identificada textualmente" : "Não identificada"}</dd></div>
    </dl>
    {!inspection.supported && <p className="mt-2 text-amber-200">{inspection.reason}</p>}
    <p role="status" className="mt-2 text-xs text-slate-400">Inspeção estática local concluída. Resolução de perfil 2D analítico profundo requer despacho assíncrono.</p>
  </details>;
}
