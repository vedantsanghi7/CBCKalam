import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

const base = "inline-flex items-center justify-center gap-2 font-medium rounded-pill transition-all active:scale-[0.98] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-indigo-200/60 disabled:opacity-50";
const variants: Record<Variant, string> = {
  primary: "bg-ink text-white hover:bg-[#1E2030]",
  ghost:   "bg-white/40 text-[var(--text-1)] hover:bg-white/70 backdrop-blur-md",
  outline: "border border-black/10 bg-white/50 text-[var(--text-1)] hover:bg-white/80 backdrop-blur-md",
};
const sizes: Record<Size, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-5 text-[15px]",
  lg: "h-13 px-6 text-base",
};

export function PillButton({
  variant = "primary", size = "md", className, ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button className={cn(base, variants[variant], sizes[size], className)} {...rest} />;
}
