export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_TIMEOUT_MS = 30_000;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly retryAfterSeconds: number | null = null
  ) {
    super(message);
  }
}

function apiErrorDetail(payload: unknown): string | null {
  if (typeof payload !== "object" || payload === null || !("detail" in payload)) {
    return null;
  }
  const detail = payload.detail;
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail)) return null;

  const messages = detail.flatMap((item) => {
    if (typeof item !== "object" || item === null || !("msg" in item)) return [];
    return typeof item.msg === "string" ? [item.msg] : [];
  });
  return messages.length > 0 ? messages.join("; ") : null;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      credentials: "include",
      headers: isFormData
        ? init?.headers
        : { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      signal: init?.signal ?? AbortSignal.timeout(API_TIMEOUT_MS)
    });
  } catch (reason) {
    if (reason instanceof DOMException && reason.name === "TimeoutError") {
      throw new ApiError("Tempo limite de comunicação com a API excedido", 408);
    }
    throw reason;
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const rawRetryAfter = response.headers.get("Retry-After");
    const retryAfter = rawRetryAfter === null ? null : Number.parseInt(rawRetryAfter, 10);
    throw new ApiError(
      apiErrorDetail(body) ?? `Request failed (${response.status})`,
      response.status,
      retryAfter !== null && Number.isFinite(retryAfter) && retryAfter >= 0
        ? retryAfter
        : null
    );
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}
