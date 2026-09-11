"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

interface NavItem {
  href: string;
  label: string;
}

export function Sidebar({ items }: { items: NavItem[] }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="flex w-60 shrink-0 flex-col justify-between border-r border-line bg-white p-5">
      <div>
        <div className="mb-8 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-flask-50 text-flask-500">⚗</div>
          <span className="font-serif text-lg text-ink">Chemgenie</span>
        </div>

        <nav className="flex flex-col gap-1">
          {items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded px-3 py-2 text-sm ${
                  active ? "bg-flask-50 text-flask-600" : "text-muted hover:bg-paper"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div>
        <div className="mb-3 border-t border-line pt-3">
          <p className="text-sm text-ink">{user?.full_name}</p>
          <p className="text-xs text-muted">
            {user?.email} · {user?.role}
          </p>
        </div>
        <button onClick={logout} className="text-sm text-muted hover:text-danger">
          Đăng xuất
        </button>
      </div>
    </aside>
  );
}
