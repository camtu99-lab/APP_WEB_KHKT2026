const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("chemgenie_access_token");
}

export function setTokens(accessToken: string, refreshToken: string) {
  window.localStorage.setItem("chemgenie_access_token", accessToken);
  window.localStorage.setItem("chemgenie_refresh_token", refreshToken);
}

export function clearTokens() {
  window.localStorage.removeItem("chemgenie_access_token");
  window.localStorage.removeItem("chemgenie_refresh_token");
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("chemgenie_refresh_token");
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  auth?: boolean; // mặc định true — hầu hết API cần token
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const token = getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const code = data?.error?.code || "UNKNOWN_ERROR";
    const message = data?.error?.message || data?.detail || "Đã xảy ra lỗi, vui lòng thử lại.";
    throw new ApiError(code, message, res.status);
  }

  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown, auth = true) => request<T>(path, { method: "POST", body, auth }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: "PATCH", body }),
};
