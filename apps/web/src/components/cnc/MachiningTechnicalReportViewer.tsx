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
  geometry_audit: {
    schema_version: "vena-ia.cnc-geometry-dimensional-audit/v1";
    status: "PASS" | "REJECTED";
    deviations: readonly {
      axis: "MAX_RADIUS" | "MIN_Z" | "MAX_Z";
      nominal_mm: number;
      programmed_mm: number;
      signed_deviation_mm: number;
      tolerance_mm: number;
      within_tolerance: boolean;
    }[];
    findings: readonly string[];
    manifest_generation_allowed: boolean;
  };
  surface_roughness_audit: {
    schema_version: "vena-ia.cnc-surface-roughness-audit/v1";
    ra_theoretical_um: number;
    rz_theoretical_um: number;
    finish_feed_mm_per_rev: number;
    insert_nose_radius_mm: number;
    nominal_ra_max_um: number | null;
    compliance_tag: "WITHIN_NOMINAL_RA_TOLERANCE" | "EXCEEDS_NOMINAL_RA_TOLERANCE" | "NOMINAL_RA_TOLERANCE_UNAVAILABLE";
    model_limitation: "IDEAL_KINEMATIC_MODEL_EXCLUDES_VIBRATION_TOOL_WEAR_AND_MATERIAL_EFFECTS";
    safety_flags: MachiningReportSafetyFlags;
  };
  power_force_audit: {
    schema_version: "vena-ia.cnc-machining-power-force-audit/v1";
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    kc1_1_n_per_mm2: number;
    kienzle_exponent_mc: number;
    feed_mm_per_rev: number;
    depth_of_cut_mm: number;
    cutting_edge_angle_deg: number;
    chip_thickness_mm: number;
    chip_width_mm: number;
    cutting_speed_m_per_min: number;
    spindle_rpm_reference: number;
    max_spindle_rpm: number;
    fc_nominal_n: number;
    pc_cutting_kw: number;
    p_motor_est_kw: number;
    mrr_cm3_min: number;
    machine_power_limit_kw: number;
    power_status: "POWER_WITHIN_LIMITS" | "POWER_EXCEEDED_WARNING";
    spindle_efficiency: 0.8;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "KIENZLE_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_DYNAMIC_EFFICIENCY";
    safety_flags: MachiningReportSafetyFlags;
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
  const dimensionalPass = report.geometry_audit.status === "PASS";
  const powerWithinLimits = report.power_force_audit.power_status === "POWER_WITHIN_LIMITS";

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

    <section aria-labelledby="report-dimensional-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-dimensional-heading" className="text-lg font-semibold">Auditoria geométrica dimensional</h2>
        <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${dimensionalPass ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {dimensionalPass ? "AUDITORIA GEOMÉTRICA CONFORME" : "DESVIO DETECTADO"}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead><tr className="border-b border-slate-700 text-slate-400">
            <th className="p-2">Dimensão</th><th className="p-2">Nominal</th><th className="p-2">Programada</th><th className="p-2">Desvio</th><th className="p-2">Tolerância</th>
          </tr></thead>
          <tbody>{report.geometry_audit.deviations.map((item) => <tr key={item.axis} className="border-b border-slate-800 font-mono">
            <td className="p-2">{item.axis}</td><td className="p-2">{item.nominal_mm.toFixed(3)} mm</td><td className="p-2">{item.programmed_mm.toFixed(3)} mm</td><td className={`p-2 ${item.within_tolerance ? "text-emerald-300" : "text-red-300"}`}>{item.signed_deviation_mm.toFixed(3)} mm</td><td className="p-2">±{item.tolerance_mm.toFixed(3)} mm</td>
          </tr>)}</tbody>
        </table>
      </div>
      <a href={`/api/v1/cnc/turning/plans/${encodeURIComponent(report.plan_id)}/report/download`} download className="inline-flex rounded-lg border border-cyan-500 bg-cyan-950 px-4 py-2 text-sm font-semibold text-cyan-100">
        Exportar laudo textual — {report.governance_stamp}
      </a>
    </section>

    <section aria-labelledby="report-roughness-heading" className="space-y-3">
      <h2 id="report-roughness-heading" className="text-lg font-semibold">Acabamento superficial teórico</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Ra teórico" value={`${report.surface_roughness_audit.ra_theoretical_um.toFixed(3)} µm`} />
        <Metric label="Rz teórico" value={`${report.surface_roughness_audit.rz_theoretical_um.toFixed(3)} µm`} />
        <Metric label="Avanço" value={`${report.surface_roughness_audit.finish_feed_mm_per_rev.toFixed(3)} mm/rot`} />
        <Metric label="Raio de ponta" value={`${report.surface_roughness_audit.insert_nose_radius_mm.toFixed(3)} mm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">{report.surface_roughness_audit.compliance_tag}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        RUGOSIDADE TEÓRICA CINEMÁTICA - NÃO CONSIDERA VIBRAÇÃO OU DESGASTE DA FERRAMENTA
      </p>
    </section>

    <section aria-labelledby="report-power-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-power-heading" className="text-lg font-semibold">Telemetria energética teórica</h2>
        <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${powerWithinLimits ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-amber-500 bg-amber-950 text-amber-100"}`}>
          {powerWithinLimits ? "POTÊNCIA ADEQUADA" : "ALERTA DE POTÊNCIA EXCESSIVA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Força tangencial estimada" value={`${report.power_force_audit.fc_nominal_n.toFixed(2)} N`} />
        <Metric label="Potência de corte" value={`${report.power_force_audit.pc_cutting_kw.toFixed(3)} kW`} />
        <Metric label="Potência estimada do motor" value={`${report.power_force_audit.p_motor_est_kw.toFixed(3)} kW`} />
        <Metric label="MRR" value={`${report.power_force_audit.mrr_cm3_min.toFixed(3)} cm³/min`} />
      </dl>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ENERGÉTICA ANALÍTICA DE KIENZLE - NÃO CONSIDERA RENDIMENTO DINÂMICO REAL
      </p>
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
