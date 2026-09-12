import type { TurningProfile2D } from "./turning-contracts";

export type DispatchPayload = Readonly<{
  fileBytes: ArrayBuffer | Blob;
  filename: string;
  schema: string;
}>;

export type DispatchJobState = "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED";

export type DispatchJobStatus = Readonly<{
  jobId: string;
  status: DispatchJobState;
  error?: string;
  profile?: TurningProfile2D;
  boundingBox?: Readonly<{
    maxRadiusMm: number;
    minZMm: number;
    maxZMm: number;
    totalZLengthMm: number;
  }>;
  reviewStatus?: "PROFILE_AVAILABLE_REQUIRES_REVIEW";
  warnings?: readonly string[];
}>;

export type DispatchTransport = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

export type CadDispatchOptions = Readonly<{
  endpoint?: string;
  statusEndpoint?: string;
  timeoutMs?: number;
  transport?: DispatchTransport;
  signal?: AbortSignal;
}>;

const DEFAULT_DISPATCH_ENDPOINT = "/api/v1/cad/step/dispatch";
const DEFAULT_STATUS_ENDPOINT = "/api/v1/cad/step/jobs";
const DEFAULT_TIMEOUT_MS = 15_000;
const jobStates = new Set<DispatchJobState>(["QUEUED", "PROCESSING", "COMPLETED", "FAILED"]);

function failed(error: string, jobId = ""): DispatchJobStatus {
  return { jobId, status: "FAILED", error };
}

function finiteNumber(value: unknown, minimum = -Infinity): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= minimum;
}

function normalizeCompletedProfile(candidate: Record<string, unknown>): Pick<DispatchJobStatus, "profile" | "boundingBox" | "reviewStatus" | "warnings"> | null {
  const rawProfile = candidate.profile_data;
  if (!rawProfile || typeof rawProfile !== "object") return null;
  const profile = rawProfile as Record<string, unknown>;
  const rawPoints = profile.points;
  const rawBounds = profile.bounding_box;
  const rawWarnings = profile.warnings ?? [];
  if (!Array.isArray(rawPoints) || rawPoints.length < 2 || !rawBounds || typeof rawBounds !== "object" ||
      !Array.isArray(rawWarnings) || rawWarnings.some(warning => typeof warning !== "string" || !warning.trim()) ||
      profile.review_status !== "PROFILE_AVAILABLE_REQUIRES_REVIEW") return null;

  const points = rawPoints.map(point => {
    if (!point || typeof point !== "object") return null;
    const rawPoint = point as Record<string, unknown>;
    return finiteNumber(rawPoint.r_mm, 0) && finiteNumber(rawPoint.z_mm)
      ? { radius_mm: rawPoint.r_mm, z_mm: rawPoint.z_mm }
      : null;
  });
  if (points.some(point => point === null)) return null;

  const bounds = rawBounds as Record<string, unknown>;
  if (!finiteNumber(bounds.max_radius_mm, 0) || !finiteNumber(bounds.min_z_mm) ||
      !finiteNumber(bounds.max_z_mm) || !finiteNumber(bounds.total_z_length_mm, 0) ||
      bounds.max_z_mm < bounds.min_z_mm) return null;

  return {
    profile: {
      points: points as Array<{ radius_mm: number; z_mm: number }>,
      axis_origin: [0, 0, 0],
      axis_direction: [0, 0, 1],
      is_closed: false,
    },
    boundingBox: {
      maxRadiusMm: bounds.max_radius_mm,
      minZMm: bounds.min_z_mm,
      maxZMm: bounds.max_z_mm,
      totalZLengthMm: bounds.total_z_length_mm,
    },
    reviewStatus: "PROFILE_AVAILABLE_REQUIRES_REVIEW",
    warnings: rawWarnings.map(warning => (warning as string).slice(0, 160)),
  };
}

function normalizeJobStatus(value: unknown, fallbackJobId = ""): DispatchJobStatus {
  if (!value || typeof value !== "object") return failed("Resposta de despacho CAD inválida.", fallbackJobId);
  const candidate = value as Record<string, unknown>;
  const rawJobId = candidate.job_id;
  const jobId = typeof rawJobId === "string" && rawJobId.trim() ? rawJobId : fallbackJobId;
  const status = candidate.status;
  if (!jobId || typeof status !== "string" || !jobStates.has(status as DispatchJobState)) {
    return failed("Resposta de despacho CAD inválida.", jobId);
  }
  const error = typeof candidate.error_detail === "string" && candidate.error_detail.trim()
    ? candidate.error_detail.slice(0, 300)
    : undefined;
  if (status === "COMPLETED") {
    const completed = normalizeCompletedProfile(candidate);
    if (!completed) return failed("Perfil RZ retornado pela API é inválido.", jobId);
    return { jobId, status, ...completed };
  }
  return error ? { jobId, status: status as DispatchJobState, error } : { jobId, status: status as DispatchJobState };
}

function normalizedOptions(options: CadDispatchOptions) {
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs <= 0) throw new Error("O timeout de despacho CAD é inválido.");
  return {
    endpoint: options.endpoint ?? DEFAULT_DISPATCH_ENDPOINT,
    timeoutMs,
    transport: options.transport ?? fetch,
    signal: options.signal,
  };
}

export function buildDispatchFormData(payload: DispatchPayload): FormData {
  const filename = payload.filename.trim();
  const schema = payload.schema.trim();
  const file = payload.fileBytes instanceof Blob
    ? payload.fileBytes
    : new Blob([payload.fileBytes], { type: "application/step" });
  if (!filename) throw new Error("O nome do arquivo STEP é obrigatório.");
  if (!schema) throw new Error("O schema STEP é obrigatório.");
  if (file.size <= 0) throw new Error("O arquivo STEP está vazio.");

  const form = new FormData();
  form.append("file", file, filename);
  return form;
}

async function requestJob(
  url: string,
  init: RequestInit,
  options: CadDispatchOptions,
  fallbackJobId = "",
): Promise<DispatchJobStatus> {
  let resolved: ReturnType<typeof normalizedOptions>;
  try {
    resolved = normalizedOptions(options);
  } catch (error) {
    return failed(error instanceof Error ? error.message : "Configuração de despacho CAD inválida.", fallbackJobId);
  }

  const controller = new AbortController();
  const abortFromCaller = () => controller.abort();
  if (resolved.signal?.aborted) controller.abort();
  else resolved.signal?.addEventListener("abort", abortFromCaller, { once: true });
  const timer = setTimeout(() => controller.abort(), resolved.timeoutMs);
  try {
    const response = await resolved.transport(url, { ...init, signal: controller.signal });
    if (!response.ok) return failed(`Despacho CAD recusado (HTTP ${response.status}).`, fallbackJobId);
    return normalizeJobStatus(await response.json(), fallbackJobId);
  } catch {
    if (resolved.signal?.aborted) return failed("O despacho CAD foi cancelado.", fallbackJobId);
    if (controller.signal.aborted) return failed("O despacho CAD excedeu o tempo limite.", fallbackJobId);
    return failed("Falha de comunicação no despacho CAD.", fallbackJobId);
  } finally {
    clearTimeout(timer);
    resolved.signal?.removeEventListener("abort", abortFromCaller);
  }
}

export async function dispatchCadJob(
  payload: DispatchPayload,
  options: CadDispatchOptions = {},
): Promise<DispatchJobStatus> {
  let body: FormData;
  try {
    body = buildDispatchFormData(payload);
  } catch (error) {
    return failed(error instanceof Error ? error.message : "Payload de despacho CAD inválido.");
  }
  const endpoint = options.endpoint ?? DEFAULT_DISPATCH_ENDPOINT;
  return requestJob(endpoint, { method: "POST", body }, options);
}

export async function pollCadDispatchJob(
  jobId: string,
  options: CadDispatchOptions = {},
): Promise<DispatchJobStatus> {
  const normalizedJobId = jobId.trim();
  if (!normalizedJobId) return failed("O identificador do job é obrigatório.");
  const endpoint = (options.statusEndpoint ?? DEFAULT_STATUS_ENDPOINT).replace(/\/$/, "");
  return requestJob(`${endpoint}/${encodeURIComponent(normalizedJobId)}`, { method: "GET" }, options, normalizedJobId);
}

export function isTerminalDispatchStatus(status: DispatchJobStatus): boolean {
  return status.status === "COMPLETED" || status.status === "FAILED";
}
