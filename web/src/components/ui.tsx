import { ReactNode } from "react";

export function Card({ title, subtitle, action, children, className = "" }: {
  title?: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`min-w-0 rounded-2xl border border-black/[0.07] bg-[var(--surface)] p-5 shadow-[0_1px_2px_rgba(0,0,0,0.04)] dark:border-white/10 ${className}`}>
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-[15px] font-semibold tracking-tight">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-sm text-[var(--muted)]">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-black/[0.07] bg-[var(--surface)] p-4 dark:border-white/10">
      <div className="text-xs font-medium uppercase tracking-wide text-[var(--muted)]">{label}</div>
      <div className="mt-1.5 text-2xl font-semibold tracking-tight">{value}</div>
      {hint && <div className="mt-1 text-xs text-[var(--ink-2)]">{hint}</div>}
    </div>
  );
}

export function Pill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "brand" | "good" | "bad" | "warn" }) {
  const tones = {
    neutral: "bg-black/[0.05] text-[var(--ink-2)] dark:bg-white/10",
    brand: "bg-brand-50 text-brand-700 dark:bg-brand-500/20 dark:text-brand-100",
    good: "bg-green-50 text-green-800 dark:bg-green-500/15 dark:text-green-300",
    bad: "bg-red-50 text-red-800 dark:bg-red-500/15 dark:text-red-300",
    warn: "bg-amber-50 text-amber-800 dark:bg-amber-500/15 dark:text-amber-200",
  };
  return <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>{children}</span>;
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton rounded-lg bg-black/[0.06] dark:bg-white/10 ${className}`} />;
}

export function Stars({ score }: { score: number }) {
  return (
    <span className="tracking-tight text-amber-500" aria-label={`nota ${score} de 5`}>
      {"★".repeat(score)}
      <span className="text-black/15 dark:text-white/20">{"★".repeat(5 - score)}</span>
    </span>
  );
}

export function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-[var(--ink-2)]">
      <span className="h-2.5 w-2.5 rounded-sm" style={{ background: color }} />
      {label}
    </span>
  );
}
