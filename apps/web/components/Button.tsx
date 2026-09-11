import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base =
    "h-10 px-4 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const styles: Record<string, string> = {
    primary: "bg-flask-500 text-white hover:bg-flask-600",
    secondary: "bg-white border border-line text-ink hover:bg-paper",
    danger: "bg-danger text-white hover:opacity-90",
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...props} />;
}
