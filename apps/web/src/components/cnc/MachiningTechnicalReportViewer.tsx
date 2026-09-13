export type CNCControllerProfile = "FANUC_0I" | "SIEMENS_840D" | "HAAS" | "SIMULATED_STUB";
export type TurningOperation = "FACING" | "ROUGH_TURNING" | "FINISHING" | "GROOVING";

export interface MachiningReportSafetyFlags {
  physical_use_authorized: false;
  g9: "PENDING_AUTHORITATIVE_REVIEW";
  no_human_review_bypass: true;
  machine_send: false;
  dnc: false;
  nc_transfer: false;
  cycle_start: false;
  emission_status: "CONTROLLER_PROFILE_UNRESOLVED";
  executable_output: false;
}

export interface MachiningReportToolBreakdown {
  tool: string;
  cutting_time_seconds: number;
  rapid_time_seconds: number;
  cutting_distance_mm: number;
  rapid_distance_mm: number;
}

export interface MachiningCycleTimeEstimate {
  total_cutting_time_seconds: number;
  total_rapid_time_seconds: number;
  total_cycle_time_seconds: number;
  total_cutting_distance_mm: number;
  total_rapid_distance_mm: number;
  rapid_feed_rate_mm_min: number;
  per_tool_breakdown: readonly MachiningReportToolBreakdown[];
  disclaimer: "THEORETICAL_ANALYTICAL_ESTIMATE_NOT_PHYSICALLY_APPROVED";
}

export interface MachiningTechnicalReportPayload {
  schema_version: "vena-ia.cnc-machining-report/v1";
  status: "REQUIRES_HUMAN_REVIEW";
  plan_id: string;
  source_plan_name: null;
  cad_job_id: string;
  controller_profile: CNCControllerProfile;
  program_number: number;
  program_sha256: string;
  analytical_snapshot_at: string;
  tools: readonly {
    tool_id: string;
    operations: readonly TurningOperation[];
  }[];
  cycle_time_estimate: MachiningCycleTimeEstimate;
  total_distance_mm: number;
  envelope_audit: "PASS_DECLARED_2D_ENVELOPE_ONLY";
  machine_envelope: {
    x_min_mm: number;
    x_max_mm: number;
    z_min_mm: number;
    z_max_mm: number;
    chuck_exclusion_zone: {
      x_min_mm: number;
      x_max_mm: number;
      z_min_mm: number;
      z_max_mm: number;
    };
  };
  chuck_proximity: {
    minimum_clearance_mm: number;
    threshold_mm: number;
    closest_segment_index: number;
    warning_code: "WARNING_PROXIMITY_CHUCK" | null;
  };
  coordinate_convention: "LATHE_X_DIAMETER_Z";
  governance_stamp: "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO";
  safety_flags: MachiningReportSafetyFlags;
  limitations: readonly string[];
}

interface MachiningTechnicalReportViewerProps {
  report: MachiningTechnicalReportPayload;
}

function duration(seconds: number): string {
  const safeSeconds = Math.max(0, Math.round(seconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const remainingSeconds = safeSeconds % 60;
  return [hours, minutes, remainingSeconds].map((value) => String(value).padStart(2, "0")).join(":");
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-slate-700 bg-slate-950 p-3">
    <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
    <dd className="mt-1 font-mono text-sm text-cyan-100">{value}</dd>
  </div>;
}

export function MachiningTechnicalReportViewer({ report }: MachiningTechnicalReportViewerProps) {
  const estimate = report.cycle_time_estimate;
  const proximityWarning = report.chuck_proximity.warning_code === "WARNING_PROXIMITY_CHUCK";

  return <article className="space-y-6 rounded-2xl border border-slate-700 bg-slate-900 p-6 text-slate-100" aria-label="Relatório técnico CNC">
    <header className="space-y-3">
      <div className="rounded-lg border-2 border-amber-400 bg-amber-950/60 p-4 text-center font-bold text-amber-100" role="alert">
        {report.governance_stamp}
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-cyan-400">{report.schema_version}</p>
        <h1 className="mt-1 text-2xl font-semibold">Relatório técnico de usinagem</h1>
        <p className="mt-1 text-sm text-slate-300">Plano {report.plan_id} · Programa {report.program_number} · {report.controller_profile}</p>
      </div>
    </header>

    <section aria-labelledby="report-cycle-heading" className="space-y-3">
      <h2 id="report-cycle-heading" className="text-lg font-semibold">Estimativa analítica</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Tempo total" value={duration(estimate.total_cycle_time_seconds)} />
        <Metric label="Tempo de corte" value={duration(estimate.total_cutting_time_seconds)} />
        <Metric label="Tempo rápido" value={duration(estimate.total_rapid_time_seconds)} />
        <Metric label="Distância total" value={`${report.total_distance_mm.toFixed(3)} mm`} />
      </dl>
      <p className="text-xs font-semibold text-amber-200">ESTIMATIVA ANALÍTICA TEÓRICA - NÃO REPRESENTA TEMPO FÍSICO HOMOLOGADO</p>
    </section>

    <section aria-labelledby="report-tools-heading" className="space-y-3">
      <h2 id="report-tools-heading" className="text-lg font-semibold">Ferramentas e operações</h2>
      <ul className="grid gap-3 md:grid-cols-2">
        {report.tools.map((tool) => <li key={tool.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-3">
          <span className="font-mono text-cyan-100">{tool.tool_id}</span>
          <span className="ml-2 text-sm text-slate-300">{tool.operations.join(" · ")}</span>
        </li>)}
      </ul>
    </section>

    <section aria-labelledby="report-audit-heading" className="space-y-3">
      <h2 id="report-audit-heading" className="text-lg font-semibold">Auditoria declarada</h2>
      <dl className="grid gap-3 sm:grid-cols-2">
        <Metric label="Envelope 2D" value={report.envelope_audit} />
        <Metric label="Folga mínima da placa" value={`${report.chuck_proximity.minimum_clearance_mm.toFixed(3)} mm`} />
      </dl>
      {proximityWarning ? <p role="alert" className="rounded-lg border border-red-500 bg-red-950/60 p-3 font-mono text-red-100">WARNING_PROXIMITY_CHUCK</p> : null}
      <p className="font-mono text-xs text-slate-400">SHA-256 do programa: {report.program_sha256}</p>
    </section>

    <section aria-labelledby="report-limits-heading" className="space-y-2">
      <h2 id="report-limits-heading" className="text-lg font-semibold">Limitações obrigatórias</h2>
      <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
        {report.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
      </ul>
      <p className="text-xs font-semibold text-amber-200">G9=PENDING_AUTHORITATIVE_REVIEW · CONTROLLER_PROFILE_UNRESOLVED · executable_output=false</p>
    </section>
  </article>;
}
