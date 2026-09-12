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
}>;

export type DispatchTransport = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

export type CadDispatchOptions = Readonly<{
  endpoint?: string;
  timeoutMs?: number;
  transport?: DispatchTransport;
  signal?: AbortSignal;
}>;

const DEFAULT_DISPATCH_ENDPOINT = "/api/cad/dispatch";
const DEFAULT_TIMEOUT_MS = 15_000;
const jobStates = new Set<DispatchJobState>(["QUEUED", "PROCESSING", "COMPLETED", "FAILED"]);

function failed(error: string, jobId = ""): DispatchJobStatus {
  return { jobId, status: "FAILED", error };
}

function normalizeJobStatus(value: unknown, fallbackJobId = ""): DispatchJobStatus {
  if (!value || typeof value !== "object") return failed("Resposta de despacho CAD inválida.", fallbackJobId);
  const candidate = value as Record<string, unknown>;
  const jobId = typeof candidate.jobId === "string" && candidate.jobId.trim() ? candidate.jobId : fallbackJobId;
  const status = candidate.status;
  if (!jobId || typeof status !== "string" || !jobStates.has(status as DispatchJobState)) {
    return failed("Resposta de despacho CAD inválida.", jobId);
  }
  const error = typeof candidate.error === "string" && candidate.error.trim()
    ? candidate.error.slice(0, 300)
    : undefined;
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
  form.append("filename", filename);
  form.append("schema", schema);
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
  const endpoint = (options.endpoint ?? DEFAULT_DISPATCH_ENDPOINT).replace(/\/$/, "");
  return requestJob(`${endpoint}/${encodeURIComponent(normalizedJobId)}`, { method: "GET" }, options, normalizedJobId);
}

export function isTerminalDispatchStatus(status: DispatchJobStatus): boolean {
  return status.status === "COMPLETED" || status.status === "FAILED";
}
