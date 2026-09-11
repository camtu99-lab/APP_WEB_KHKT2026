"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, clearTokens, setTokens } from "./api";

export type Role = "STUDENT" | "TEACHER" | "ADMIN";

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<CurrentUser>;
  register: (email: string, fullName: string, password: string, role: Role) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== "undefined" ? window.localStorage.getItem("chemgenie_access_token") : null;
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get<CurrentUser>("/api/v1/users/me")
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string): Promise<CurrentUser> {
    const tokens = await api.post<TokenResponse>("/api/v1/auth/login", { email, password }, false);
    setTokens(tokens.access_token, tokens.refresh_token);
    const me = await api.get<CurrentUser>("/api/v1/users/me");
    setUser(me);
    return me;
  }

  async function register(email: string, fullName: string, password: string, role: Role) {
    await api.post(
      "/api/v1/auth/register",
      { email, full_name: fullName, password, role },
      false
    );
  }

  function logout() {
    clearTokens();
    setUser(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth phải được dùng bên trong AuthProvider");
  return ctx;
}
