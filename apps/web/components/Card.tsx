import { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded border border-line bg-white p-5 ${className}`}>{children}</div>;
}

export function Callout({
  tone = "info",
  children,
}: {
  tone?: "info" | "error" | "success";
  children: ReactNode;
}) {
  const styles = {
    info: "bg-flask-50 text-flask-600 border-flask-100",
    error: "bg-[#F7E9E5] text-danger border-[#EFD3CB]",
    success: "bg-[#E9F3EC] text-flask-600 border-flask-100",
  };
  return <div className={`rounded border px-4 py-3 text-sm ${styles[tone]}`}>{children}</div>;
}
