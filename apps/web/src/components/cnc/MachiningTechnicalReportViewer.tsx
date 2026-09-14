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
  tool_life_audits: readonly {
    schema_version: "vena-ia.cnc-tool-life-taylor-audit/v1";
    tool_id: string;
    tool_material_pair: "CARBIDE_P20_P30_CARBON_STEEL" | "CARBIDE_K10_ALUMINUM_6061_T6";
    cutting_speed_vc_m_per_min: number;
    taylor_n: number;
    taylor_c: number;
    effective_cutting_time_minutes: number;
    estimated_tool_life_minutes: number;
    tool_life_consumed_percent: number;
    integrity_status: "TOOL_LIFE_SAFE" | "TOOL_LIFE_EXHAUSTED_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "TAYLOR_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_THERMAL_AND_LUBRICATION_VARIATION";
    safety_flags: MachiningReportSafetyFlags;
  }[];
  cost_time_audit: {
    schema_version: "vena-ia.cnc-machining-cost-time-audit/v1";
    cost_profile: "BRL_STANDARD" | "USD_STANDARD";
    total_cycle_time_minutes: number;
    cutting_time_minutes: number;
    rapid_time_minutes: number;
    tool_change_count: number;
    tool_change_time_minutes_each: number;
    tool_change_time_minutes: number;
    setup_count: number;
    nominal_setup_time_minutes_each: number;
    nominal_setup_time_minutes: number;
    estimated_total_cost: number;
    machine_cost_component: number;
    tooling_wear_cost_component: number;
    machine_hourly_rate: number;
    cutting_edge_cost: number;
    currency: "BRL" | "USD";
    per_tool_wear_costs: readonly {
      tool_id: string;
      effective_cutting_time_minutes: number;
      estimated_tool_life_minutes: number;
      consumed_fraction: number;
      cutting_edge_cost: number;
      estimated_wear_cost: number;
    }[];
    is_theoretical_estimate: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_COST_TIME_EXCLUDES_LOGISTICS_UNPLANNED_DOWNTIME_AND_TAXES";
    safety_flags: MachiningReportSafetyFlags;
  };
  sustainability_audit: {
    schema_version: "vena-ia.cnc-machining-sustainability-audit/v1";
    electrical_energy_kwh: number;
    cutting_energy_kwh: number;
    standby_energy_kwh: number;
    carbon_emission_kg_co2e: number;
    grid_region: "BRASIL_SIN" | "USA_AVG" | "EU_AVG";
    grid_emission_factor_kg_co2e_per_kwh: number;
    motor_power_kw: number;
    standby_power_kw: number;
    cutting_time_minutes: number;
    total_cycle_time_minutes: number;
    electrical_efficiency: number;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_ENERGY_CARBON_EXCLUDES_EXTERNAL_COOLING_AND_STARTUP_PEAKS";
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

    <section aria-labelledby="report-tool-life-heading" className="space-y-3">
      <h2 id="report-tool-life-heading" className="text-lg font-semibold">Vida útil teórica das ferramentas</h2>
      <ul className="space-y-3">
        {report.tool_life_audits.map((audit) => {
          const safe = audit.integrity_status === "TOOL_LIFE_SAFE";
          const progress = Math.min(100, Math.max(0, audit.tool_life_consumed_percent));
          return <li key={audit.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-cyan-100">{audit.tool_id}</span>
              <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${safe ? "border-emerald-500 text-emerald-100" : "border-red-500 text-red-100"}`}>
                {safe ? "VIDA ÚTIL SEGURA" : "ALERTA: DESGASTE CRÍTICO"}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-300">Vida estimada: {audit.estimated_tool_life_minutes.toFixed(2)} min · Consumo: {audit.tool_life_consumed_percent.toFixed(2)}%</p>
            <div role="progressbar" aria-label={`Consumo de vida útil ${audit.tool_id}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
              <div className={safe ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${progress}%` }} />
            </div>
          </li>;
        })}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE TAYLOR - NÃO CONSIDERA FLUTUAÇÕES TÉRMICAS REAIS OU LUBRIFICAÇÃO
      </p>
    </section>

    <section aria-labelledby="report-cost-time-heading" className="space-y-3">
      <h2 id="report-cost-time-heading" className="text-lg font-semibold">Resumo econômico e de tempo</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Metric label="Tempo total estimado" value={`${report.cost_time_audit.total_cycle_time_minutes.toFixed(2)} min`} />
        <Metric label="Corte efetivo" value={`${report.cost_time_audit.cutting_time_minutes.toFixed(2)} min`} />
        <Metric label="Avanço em vazio" value={`${report.cost_time_audit.rapid_time_minutes.toFixed(2)} min`} />
        <Metric label="Trocas de ferramenta" value={`${report.cost_time_audit.tool_change_time_minutes.toFixed(2)} min`} />
        <Metric label="Setup nominal" value={`${report.cost_time_audit.nominal_setup_time_minutes.toFixed(2)} min`} />
      </dl>
      <dl className="grid gap-3 sm:grid-cols-3">
        <Metric label="Custo de máquina" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.machine_cost_component.toFixed(2)}`} />
        <Metric label="Depreciação de insertos" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.tooling_wear_cost_component.toFixed(2)}`} />
        <Metric label="Custo total estimado" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.estimated_total_cost.toFixed(2)}`} />
      </dl>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ECONÔMICA E DE TEMPO ANALÍTICA - NÃO CONSIDERA FLUTUAÇÕES LOGÍSTICAS, PARADAS NÃO PROGRAMADAS OU IMPOSTOS
      </p>
    </section>

    <section aria-labelledby="report-sustainability-heading" className="space-y-3">
      <h2 id="report-sustainability-heading" className="text-lg font-semibold">Resumo ecológico e energético</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Consumo elétrico previsto" value={`${report.sustainability_audit.electrical_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Energia de corte" value={`${report.sustainability_audit.cutting_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Energia em espera" value={`${report.sustainability_audit.standby_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Pegada de carbono" value={`${report.sustainability_audit.carbon_emission_kg_co2e.toFixed(4)} kg CO2e`} />
      </dl>
      <div aria-label="Matriz energética regional informativa" className="flex flex-wrap gap-2">
        {([
          ["BRASIL_SIN", "Brasil"],
          ["USA_AVG", "EUA"],
          ["EU_AVG", "Europa"],
        ] as const).map(([region, label]) => <span key={region} aria-current={report.sustainability_audit.grid_region === region ? "true" : undefined} className={`rounded-full border px-3 py-1 text-xs ${report.sustainability_audit.grid_region === region ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-slate-600 text-slate-400"}`}>
          {label} · {region}
        </span>)}
      </div>
      <p className="font-mono text-xs text-slate-300">Fator da matriz: {report.sustainability_audit.grid_emission_factor_kg_co2e_per_kwh.toFixed(3)} kg CO2e/kWh</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ECOLÓGICA E ENERGÉTICA ANALÍTICA - NÃO CONSIDERA DINÂMICA AUXILIAR DE REFRIGERAÇÃO EXTERNA OU PICOS DE PARTIDA
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
