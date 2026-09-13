import { SimulationWorkspace } from "../../../src/components/cnc/SimulationWorkspace";
import type { ToolpathSimulationPayload } from "../../../src/components/cnc/ToolpathCanvasViewer";

const ISO_BLOCKS = [
  "N20 G00 X50.000 Z5.000",
  "N30 G00 X42.000 Z2.000",
  "N40 G01 X38.000 Z-25.000 F0.200",
  "N50 G01 X34.000 Z-55.000 F0.180",
] as const;

const AUDIT_PAYLOAD: ToolpathSimulationPayload = {
  status: "SIMULATION_READY_REQUIRES_REVIEW",
  source_plan_id: "audit-workspace-fixture",
  controller_profile: "SIMULATED_STUB",
  coordinate_convention: "LATHE_X_DIAMETER_Z",
  machine_envelope: {
    x_min_mm: 0,
    x_max_mm: 100,
    z_min_mm: -200,
    z_max_mm: 100,
    chuck_exclusion_zone: { x_min_mm: 0, x_max_mm: 100, z_min_mm: 55, z_max_mm: 100 },
  },
  stock: { diameter_mm: 52, z_min_mm: -100, z_max_mm: 1 },
  chuck_proximity: { minimum_clearance_mm: 50, threshold_mm: 5, closest_segment_index: 0, warning_code: null },
  segments: [
    { motion_type: "RAPID", x_start_mm: 50, z_start_mm: 5, x_end_mm: 42, z_end_mm: 2, feed: null, active_tool: "T0101" },
    { motion_type: "LINEAR", x_start_mm: 42, z_start_mm: 2, x_end_mm: 38, z_end_mm: -25, feed: 0.2, active_tool: "T0101" },
    { motion_type: "LINEAR", x_start_mm: 38, z_start_mm: -25, x_end_mm: 34, z_end_mm: -55, feed: 0.18, active_tool: "T0101" },
  ],
  safety_flags: {
    physical_use_authorized: false,
    g9: "PENDING_AUTHORITATIVE_REVIEW",
    no_human_review_bypass: true,
    machine_send: false,
    dnc: false,
    nc_transfer: false,
    cycle_start: false,
    emission_status: "CONTROLLER_PROFILE_UNRESOLVED",
    executable_output: false,
  },
};

export default function CncSimulationPage() {
  return <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:px-8">
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-widest text-cyan-400">SIM Route 3</p>
        <h1 className="text-3xl font-semibold tracking-tight">CNC Toolpath Audit Workspace</h1>
        <p className="text-slate-300">Visualização sincronizada para revisão humana de trajetória, telemetria e blocos ISO.</p>
      </header>
      <SimulationWorkspace payload={AUDIT_PAYLOAD} isoBlocks={ISO_BLOCKS} />
    </div>
  </main>;
}
