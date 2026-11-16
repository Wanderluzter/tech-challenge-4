import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Cpu } from "lucide-react";
import { fmt, ModelStatus } from "../api";

export const STATE_LABEL: Record<ModelStatus["estado"], string> = {
  disponivel: "Disponível",
  sem_cota: "Sem cota",
  erro: "Com erro",
};

export function StateDot({ estado }: { estado: ModelStatus["estado"] }) {
  const color = estado === "disponivel" ? "bg-[var(--good)]" : estado === "sem_cota" ? "bg-[var(--warning)]" : "bg-[var(--critical)]";
  return <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${color}`} aria-hidden />;
}

/** Primeiro modelo disponível da lista, na ordem configurada. */
export function firstAvailable(models: ModelStatus[], except?: string | null) {
  return models.find((m) => m.estado === "disponivel" && m.modelo !== except) ?? null;
}

export default function ModelSelector({ models, selected, onSelect }: {
  models: ModelStatus[];
  selected: string | null;
  onSelect: (model: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = models.find((m) => m.modelo === selected) ?? models[0];

  useEffect(() => {
    const close = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", close); document.removeEventListener("keydown", esc); };
  }, []);

  if (!current) return null;
  return (
    <div ref={ref} className="relative">
      <button type="button" onClick={() => setOpen((o) => !o)} aria-haspopup="listbox" aria-expanded={open}
        className="flex items-center gap-2 rounded-full border border-black/10 bg-[var(--surface)] py-1 pl-2.5 pr-2 text-xs font-medium text-[var(--ink-2)] transition hover:border-black/20 dark:border-white/15">
        <StateDot estado={current.estado} />
        <span className="max-w-[160px] truncate">{current.modelo}</span>
        <ChevronDown size={13} className={`transition ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div role="listbox" className="absolute right-0 z-30 mt-2 w-80 overflow-hidden rounded-xl border border-black/10 bg-[var(--surface)] p-1.5 shadow-[0_12px_32px_rgba(0,0,0,0.14)] dark:border-white/15">
          <div className="flex items-center gap-1.5 px-2.5 pb-1.5 pt-1 text-[11px] font-medium uppercase tracking-wide text-[var(--muted)]">
            <Cpu size={12} /> Modelo de geração
          </div>
          {models.map((m) => {
            const active = m.modelo === current.modelo;
            return (
              <button key={m.modelo} role="option" aria-selected={active} type="button"
                onClick={() => { onSelect(m.modelo); setOpen(false); }}
                className={`flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition hover:bg-black/[0.04] dark:hover:bg-white/5 ${active ? "bg-black/[0.03] dark:bg-white/5" : ""}`}>
                <span className="mt-1.5"><StateDot estado={m.estado} /></span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-1.5">
                    <span className="truncate font-medium">{m.modelo}</span>
                    {m.principal && <span className="rounded bg-black/[0.05] px-1 text-[10px] text-[var(--muted)] dark:bg-white/10">padrão</span>}
                  </span>
                  <span className="block text-xs text-[var(--muted)]">
                    {STATE_LABEL[m.estado]}
                    {m.estado !== "disponivel" && m.desde ? ` desde ${fmt.time(m.desde)}` : ""}
                    {m.erro ? ` · ${m.erro}` : ""}
                  </span>
                </span>
                {active && <Check size={16} className="mt-0.5 shrink-0 text-brand-500" />}
              </button>
            );
          })}
          <p className="border-t border-black/5 px-2.5 pb-1 pt-2 text-[11px] leading-snug text-[var(--muted)] dark:border-white/10">
            Se o modelo escolhido estiver sem cota, a resposta é gerada pelo próximo disponível, com aviso.
          </p>
        </div>
      )}
    </div>
  );
}
