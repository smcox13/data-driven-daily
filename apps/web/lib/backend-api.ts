const API_BASE_URL = process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export class BackendRequestError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "BackendRequestError";
    this.status = status;
    this.body = body;
  }
}

function buildUrl(path: string) {
  return `${API_BASE_URL}/api${path}`;
}

export async function backendRequest(path: string, init: RequestInit = {}) {
  const response = await fetch(buildUrl(path), {
    ...init,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {})
    }
  });

  return response;
}

export async function backendJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await backendRequest(path, init);
  const text = await response.text();
  const body = text ? (JSON.parse(text) as unknown) : null;

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string"
        ? body.detail
        : `Backend request failed with status ${response.status}`;
    throw new BackendRequestError(detail, response.status, body);
  }

  return body as T;
}

