import { FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AlertTriangle, ArrowRight, ChevronDown, Cpu, Filter, Loader2, Search, ShieldAlert, Sparkles, X,
} from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { api, AskResult, Evidence, Filters, fmt, Meta, ModelStatus } from "../api";
import { firstAvailable, STATE_LABEL } from "../components/ModelSelector";
import { Card, Pill, Skeleton, Stars } from "../components/ui";

const DELIVERY: Record<string, string> = { no_prazo: "No prazo", atrasada: "Atrasada", nao_entregue: "Sem entrega" };
const CITATION = /\[(\d+(?:\s*(?:,|e)\s*\d+)*)\]/g;

// [1, 2] → links #ev-1 #ev-2, renderizados como chips clicáveis
function linkCitations(markdown: string): string {
  return markdown.replace(CITATION, (_, group: string) =>
    (group.match(/\d+/g) ?? []).map((n) => `[${n}](#ev-${n})`).join(" "),
  );
}

function countFilters(f: Filters) {
  return Object.values(f).filter((v) => v !== undefined && !(Array.isArray(v) && v.length === 0)).length;
}

// ------------------------------------------------------------------ filtros
function FilterPanel({ meta, filters, setFilters, topK, setTopK }: {
  meta: Meta;
  filters: Filters;
  setFilters: (f: Filters) => void;
  topK: number;
  setTopK: (k: number) => void;
}) {
  const score = filters.review_score ?? { gte: 1, lte: 5 };
  const select = "w-full rounded-lg border border-black/10 bg-transparent px-2.5 py-1.5 text-sm dark:border-white/15 dark:bg-[var(--surface)]";
  const label = "mb-1 block text-xs font-medium text-[var(--muted)]";
  const update = (patch: Partial<Filters>) => {
    const next = { ...filters, ...patch } as Filters;
    (Object.keys(next) as (keyof Filters)[]).forEach((k) => next[k] === undefined && delete next[k]);
    setFilters(next);
  };
  return (
    <div className="grid gap-4 rounded-xl border border-black/[0.07] bg-[var(--surface)] p-4 sm:grid-cols-2 lg:grid-cols-6 dark:border-white/10">
      <div>
        <span className={label}>Nota</span>
        <div className="flex items-center gap-1.5">
          <select className={select} value={score.gte}
            onChange={(e) => { const gte = +e.target.value; const s = { gte, lte: Math.max(gte, score.lte) };
              update({ review_score: s.gte === 1 && s.lte === 5 ? undefined : s }); }}>
            {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
          <span className="text-xs text-[var(--muted)]">a</span>
          <select className={select} value={score.lte}
            onChange={(e) => { const lte = +e.target.value; const s = { gte: Math.min(score.gte, lte), lte };
              update({ review_score: s.gte === 1 && s.lte === 5 ? undefined : s }); }}>
            {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </div>
      <div>
        <span className={label}>Ano da compra</span>
        <select className={select} value={filters.ano ?? ""} onChange={(e) => update({ ano: e.target.value ? +e.target.value : undefined })}>
          <option value="">Todos</option>
          {meta.anos.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>
      <div className="lg:col-span-2">
        <span className={label}>Categoria</span>
        <select className={select} value={filters.categoria ?? ""} onChange={(e) => update({ categoria: e.target.value || undefined })}>
          <option value="">Todas</option>
          {meta.categorias.map((c) => <option key={c} value={c}>{fmt.category(c)}</option>)}
        </select>
      </div>
      <div>
        <span className={label}>Estado (UF)</span>
        <select className={select} value={filters.uf ?? ""} onChange={(e) => update({ uf: e.target.value || undefined })}>
          <option value="">Todos</option>
          {meta.ufs.map((u) => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>
      <div>
        <span className={label}>Avaliações no contexto: {topK}</span>
        <input type="range" min={4} max={20} value={topK} onChange={(e) => setTopK(+e.target.value)} className="w-full accent-[var(--series-1)]" />
      </div>
      <div className="sm:col-span-2 lg:col-span-6">
        <span className={label}>Situação da entrega</span>
        <div className="flex flex-wrap gap-2">
          {meta.entrega.map(({ valor, rotulo }) => {
            const on = filters.entrega_status?.includes(valor) ?? false;
            return (
              <button key={valor} type="button"
                onClick={() => { const cur = filters.entrega_status ?? [];
                  const next = on ? cur.filter((v) => v !== valor) : [...cur, valor];
                  update({ entrega_status: next.length ? next : undefined }); }}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition ${on
                  ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/20 dark:text-brand-100"
                  : "border-black/10 text-[var(--ink-2)] hover:border-black/20 dark:border-white/15"}`}>
                {rotulo}
              </button>
            );
          })}
          {countFilters(filters) > 0 && (
            <button type="button" onClick={() => setFilters({})} className="ml-auto inline-flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--ink)]">
              <X size={12} /> Limpar filtros
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ evidências
function EvidenceCard({ ev, cited, active }: { ev: Evidence; cited: boolean; active: boolean }) {
  const delay = ev.entrega_status === "atrasada" && ev.dias_atraso ? ` (+${ev.dias_atraso} dias)` : "";
  return (
    <article id={`ev-${ev.ref}`}
      className={`scroll-mt-24 rounded-xl border p-4 transition ${active
        ? "border-brand-500 ring-2 ring-brand-500/20"
        : "border-black/[0.07] dark:border-white/10"} ${cited ? "" : "opacity-70"}`}>
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className={`grid h-6 min-w-6 place-items-center rounded-md px-1 text-xs font-semibold ${cited
          ? "bg-brand-500 text-white" : "bg-black/[0.06] text-[var(--ink-2)] dark:bg-white/10"}`}>{ev.ref}</span>
        <Stars score={ev.review_score} />
        {cited && <Pill tone="brand">citada</Pill>}
        <span className="ml-auto text-xs tabular text-[var(--muted)]">similaridade {ev.similarity.toFixed(2)}</span>
      </div>
      <p className="mt-2.5 text-[15px] leading-relaxed">“{ev.texto}”</p>
      <div className="mt-2.5 flex flex-wrap gap-x-3 gap-y-1 text-xs text-[var(--muted)]">
        <span>{ev.data_compra}</span>
        <span>{fmt.category(ev.categoria)}</span>
        <span>{ev.uf}</span>
        <span>entrega: {DELIVERY[ev.entrega_status] ?? ev.entrega_status}{delay}</span>
        <span className="tabular" title="Posição da avaliação em cada busca antes da fusão (RRF)">
          rank vetorial {ev.dense_rank ?? "—"} · rank BM25 {ev.bm25_rank ?? "—"}
        </span>
        <span className="font-mono" title={ev.review_id}>{ev.review_id.slice(0, 10)}…</span>
      </div>
    </article>
  );
}

// ------------------------------------------------------------------ rastro do pipeline
function Step({ n, title, children }: { n: number; title: string; children: ReactNode }) {
  return (
    <li className="relative pl-8">
      <span className="absolute left-0 top-0 grid h-5 w-5 place-items-center rounded-full bg-black/[0.06] text-[11px] font-semibold text-[var(--ink-2)] dark:bg-white/10">{n}</span>
      <div className="text-sm font-medium">{title}</div>
      <div className="mt-1.5 text-sm text-[var(--ink-2)]">{children}</div>
    </li>
  );
}

function Trace({ result }: { result: AskResult }) {
  const r = result.retrieval;
  const funnel = [
    { label: "Densa", value: r.n_dense },
    { label: "BM25", value: r.n_bm25 },
    { label: "Únicos", value: r.n_candidates },
    { label: "≥ limiar", value: r.n_above_threshold },
    { label: "Contexto", value: result.evidences.length },
  ];
  const max = Math.max(...funnel.map((f) => f.value), 1);
  const themes = r.stats?.temas ?? [];
  const filterEntries = Object.entries(result.filters);
  return (
    <Card title="Como chegamos aqui" subtitle="Cada etapa do pipeline RAG para esta pergunta">
      <ol className="grid gap-5">
        <Step n={1} title="Transformação da pergunta">
          <code className="block rounded-lg bg-black/[0.04] px-2.5 py-1.5 text-[13px] dark:bg-white/5">{result.parsed.search_text}</code>
          {r.queries.length > 1 && (
            <div className="mt-2 text-xs">
              Pergunta ampla, expandida em {r.queries.length} sub-buscas:
              <ul className="mt-1 grid gap-0.5">{r.queries.map((q) => <li key={q}>→ {q}</li>)}</ul>
            </div>
          )}
        </Step>
        <Step n={2} title="Filtros aplicados">
          {filterEntries.length ? (
            <div className="flex flex-wrap gap-1.5">
              {filterEntries.map(([k, v]) => (
                <Pill key={k}>{k}: {typeof v === "object" && !Array.isArray(v) ? `${v.gte}–${v.lte}` : Array.isArray(v) ? v.join(", ") : String(v)}</Pill>
              ))}
            </div>
          ) : <span className="text-xs">Nenhum — busca em toda a base</span>}
        </Step>
        <Step n={3} title="Recuperação híbrida (densa + BM25)">
          <div className="grid gap-1.5">
            {funnel.map((f) => (
              <div key={f.label} className="flex items-center gap-2 text-xs">
                <span className="w-16 shrink-0 text-[var(--muted)]">{f.label}</span>
                <div className="h-2 flex-1 rounded-full bg-black/[0.04] dark:bg-white/5">
                  <div className="h-2 rounded-full bg-[var(--series-1)]" style={{ width: `${(f.value / max) * 100}%` }} />
                </div>
                <span className="w-8 text-right tabular">{f.value}</span>
              </div>
            ))}
          </div>
          <div className="mt-2 text-xs text-[var(--muted)] tabular">
            sim. máx {r.max_similarity.toFixed(3)} · suporte {r.support_similarity.toFixed(3)} · limiar {r.min_similarity.toFixed(3)}
          </div>
        </Step>
        {themes.length > 0 && (
          <Step n={4} title={`Panorama do recorte — ${fmt.int(r.stats.total ?? 0)} avaliações`}>
            <div className="grid gap-1.5">
              {themes.slice(0, 6).map((t) => (
                <div key={t.tema} className="flex items-center justify-between gap-3 text-xs">
                  <span className="truncate">{t.rotulo}</span>
                  <span className="shrink-0 tabular text-[var(--muted)]">{fmt.int(t.n)} · {fmt.pct(t.pct)}</span>
                </div>
              ))}
            </div>
            <div className="mt-1.5 text-[11px] text-[var(--muted)]">Contagem aproximada por palavras-chave.</div>
          </Step>
        )}
        {result.context && (
          <Step n={5} title="Contexto enviado ao modelo">
            <details className="group">
              <summary className="flex cursor-pointer list-none items-center gap-1 text-xs text-brand-600 dark:text-brand-100">
                <ChevronDown size={14} className="transition group-open:rotate-180" /> Ver texto completo
              </summary>
              <pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap rounded-lg bg-black/[0.04] p-3 text-[11px] leading-relaxed dark:bg-white/5">{result.context}</pre>
            </details>
          </Step>
        )}
      </ol>
      <div className="mt-5 border-t border-black/5 pt-3 text-xs text-[var(--muted)] dark:border-white/10 tabular">
        {Object.entries(result.timings_ms).map(([k, v]) => `${k} ${fmt.ms(v)}`).join(" · ")}
        {result.model && result.model !== "nenhum" && ` · ${result.model}`}
      </div>
    </Card>
  );
}

// ------------------------------------------------------------------ avisos de modelo
const MODEL_WARNING = /indisponível/;

function ModelNotice({ result, models, onUse, onRetry }: {
  result: AskResult;
  models: ModelStatus[];
  onUse: (model: string) => void;
  onRetry: (model: string) => void;
}) {
  const box = "flex flex-wrap items-center gap-x-3 gap-y-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-100";
  const button = "rounded-lg bg-amber-900/10 px-2.5 py-1 text-xs font-medium hover:bg-amber-900/20 dark:bg-white/10 dark:hover:bg-white/20";
  if (result.provider === "extractive_fallback") {
    const next = firstAvailable(models);
    return (
      <div className={box} role="status">
        <AlertTriangle size={16} className="shrink-0" />
        <span className="min-w-0 flex-1">
          <strong>Nenhum modelo respondeu.</strong> {result.warnings.find((w) => MODEL_WARNING.test(w))} As evidências abaixo são da busca, sem síntese.
        </span>
        {next
          ? <button type="button" className={button} onClick={() => onRetry(next.modelo)}>Tentar de novo com {next.modelo}</button>
          : <span className="text-xs">Todos os modelos estão sem cota; tente mais tarde ou ajuste <code>LLM_FALLBACK_MODELS</code>.</span>}
      </div>
    );
  }
  if (result.requested_model && result.model && result.model !== "nenhum" && result.model !== result.requested_model) {
    const reason = models.find((m) => m.modelo === result.requested_model);
    return (
      <div className={box} role="status">
        <Cpu size={16} className="shrink-0" />
        <span className="min-w-0 flex-1">
          <strong>{result.requested_model}</strong> {reason && reason.estado !== "disponivel" ? `está ${STATE_LABEL[reason.estado].toLowerCase()}` : "não respondeu"}
          {reason?.erro ? ` (${reason.erro})` : ""}. Esta resposta foi gerada por <strong>{result.model}</strong>.
        </span>
        <button type="button" className={button} onClick={() => onUse(result.model)}>Usar {result.model} nas próximas</button>
      </div>
    );
  }
  return null;
}

// ------------------------------------------------------------------ página
export default function AskPage({ meta, models, model, setModel, refreshModels }: {
  meta: Meta | null;
  models: ModelStatus[];
  model: string | null;
  setModel: (model: string) => void;
  refreshModels: () => void;
}) {
  const [question, setQuestion] = useState("");
  const [filters, setFilters] = useState<Filters>({});
  const [topK, setTopK] = useState(12);
  const [showFilters, setShowFilters] = useState(false);
  const [onlyCited, setOnlyCited] = useState(false);
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResult | null>(null);
  const [activeRef, setActiveRef] = useState<number | null>(null);
  const timer = useRef<number>();

  const [params, setParams] = useSearchParams();
  const ran = useRef(false);

  useEffect(() => { if (meta) setTopK(meta.top_k); }, [meta]);
  // ?q=... abre já com a pergunta respondida (link compartilhável)
  useEffect(() => {
    const q = params.get("q");
    if (q && !ran.current) { ran.current = true; submit(q); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function submit(text = question, modelOverride?: string) {
    const q = text.trim();
    if (!q || loading) return;
    setQuestion(q);
    setParams({ q }, { replace: true });
    setLoading(true); setError(null); setActiveRef(null); setElapsed(0);
    const start = Date.now();
    timer.current = window.setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 500);
    try {
      setResult(await api.ask(q, filters, topK, modelOverride ?? model));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      window.clearInterval(timer.current);
      setLoading(false);
      refreshModels(); // a pergunta pode ter revelado um modelo sem cota
    }
  }

  const answerMd = useMemo(() => (result?.status === "ok" ? linkCitations(result.answer) : ""), [result]);
  const cited = new Set(result?.cited_refs ?? []);
  const evidences = (result?.evidences ?? []).filter((ev) => !onlyCited || cited.has(ev.ref));
  const nFilters = countFilters(filters);

  function focusEvidence(ref: number) {
    setOnlyCited(false);
    setActiveRef(ref);
    requestAnimationFrame(() => document.getElementById(`ev-${ref}`)?.scrollIntoView({ behavior: "smooth", block: "center" }));
  }

  return (
    <div className="grid gap-6">
      {/* busca */}
      <div className={`mx-auto w-full transition-all ${result || loading ? "max-w-none" : "max-w-3xl pt-8 sm:pt-16"}`}>
        {!result && !loading && (
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">O que seus clientes estão dizendo?</h1>
            <p className="mx-auto mt-3 max-w-xl text-[15px] text-[var(--ink-2)]">
              Pergunte em linguagem natural. Cada resposta é gerada só a partir das avaliações recuperadas e cita as que a sustentam.
            </p>
          </div>
        )}
        <form onSubmit={(e: FormEvent) => { e.preventDefault(); submit(); }}
          className="flex items-center gap-2 rounded-2xl border border-black/10 bg-[var(--surface)] p-2 shadow-[0_2px_12px_rgba(0,0,0,0.05)] focus-within:border-brand-500 focus-within:ring-4 focus-within:ring-brand-500/10 dark:border-white/15">
          <Search size={18} className="ml-2 shrink-0 text-[var(--muted)]" />
          <input value={question} onChange={(e) => setQuestion(e.target.value)} maxLength={500}
            placeholder="Ex.: o que os clientes dizem sobre atraso na entrega?"
            className="min-w-0 flex-1 bg-transparent px-1 py-2 text-[15px] outline-none placeholder:text-[var(--muted)]" />
          <button type="button" onClick={() => setShowFilters((s) => !s)}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-medium transition ${showFilters || nFilters
              ? "bg-brand-50 text-brand-700 dark:bg-brand-500/20 dark:text-brand-100" : "text-[var(--ink-2)] hover:bg-black/5 dark:hover:bg-white/5"}`}>
            <Filter size={15} /> <span className="hidden sm:inline">Filtros</span>{nFilters > 0 && <span className="tabular">({nFilters})</span>}
          </button>
          <button type="submit" disabled={!question.trim() || loading}
            className="inline-flex items-center gap-1.5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-40">
            {loading ? <Loader2 size={15} className="animate-spin" /> : <ArrowRight size={15} />}
            <span className="hidden sm:inline">Perguntar</span>
          </button>
        </form>
        {(() => {
          const current = models.find((m) => m.modelo === model);
          if (!current || current.estado === "disponivel" || loading) return null;
          const next = firstAvailable(models, current.modelo);
          return (
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-amber-800 dark:text-amber-200">
              <AlertTriangle size={14} />
              <span><strong>{current.modelo}</strong> está {STATE_LABEL[current.estado].toLowerCase()}{current.desde ? ` desde ${fmt.time(current.desde)}` : ""}. As perguntas usarão o próximo modelo disponível.</span>
              {next && (
                <button type="button" onClick={() => setModel(next.modelo)}
                  className="rounded-md border border-amber-300 px-2 py-0.5 font-medium hover:bg-amber-50 dark:border-amber-500/40 dark:hover:bg-amber-500/10">
                  Trocar para {next.modelo}
                </button>
              )}
            </div>
          );
        })()}
        {showFilters && meta && (
          <div className="mt-3">
            <FilterPanel meta={meta} filters={filters} setFilters={setFilters} topK={topK} setTopK={setTopK} />
          </div>
        )}
        {meta && (
          <div className={`mt-4 flex flex-wrap gap-2 ${result || loading ? "" : "justify-center"}`}>
            {meta.exemplos.map((ex) => (
              <button key={ex} type="button" onClick={() => submit(ex)} disabled={loading}
                className="rounded-full border border-black/10 bg-[var(--surface)] px-3 py-1.5 text-left text-xs text-[var(--ink-2)] transition hover:border-brand-500 hover:text-brand-700 disabled:opacity-50 dark:border-white/15 dark:hover:text-white">
                {ex}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
          <AlertTriangle size={16} className="mt-0.5 shrink-0" /> {error}
        </div>
      )}

      {result && !loading && (
        <ModelNotice result={result} models={models} onUse={setModel}
          onRetry={(m) => { setModel(m); submit(result.question, m); }} />
      )}

      {loading && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <Card title={<span className="inline-flex items-center gap-2"><Loader2 size={16} className="animate-spin text-brand-500" /> Analisando avaliações…</span>}
            subtitle={elapsed < 2 ? "Recuperando as avaliações mais relevantes" : `Gerando a resposta com ${model ?? "o LLM"} · ${elapsed}s`}>
            <div className="grid gap-3"><Skeleton className="h-4 w-11/12" /><Skeleton className="h-4 w-10/12" /><Skeleton className="h-4 w-9/12" /><Skeleton className="h-4 w-10/12" /></div>
          </Card>
          <Card><div className="grid gap-3"><Skeleton className="h-4 w-1/2" /><Skeleton className="h-16" /><Skeleton className="h-24" /></div></Card>
        </div>
      )}

      {result && !loading && (
        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <div className="grid gap-6">
            {result.status === "ok" ? (
              <Card title={<span className="inline-flex items-center gap-2"><Sparkles size={16} className="text-brand-500" /> Resposta</span>}
                subtitle={result.question}>
                <div className="answer text-[15px] leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ href, children }) => {
                        const ref = href?.startsWith("#ev-") ? Number(href.slice(4)) : null;
                        if (ref === null) return <a href={href} className="text-brand-600 underline">{children}</a>;
                        return (
                          <button type="button" onClick={() => focusEvidence(ref)}
                            className="mx-0.5 inline-grid h-5 min-w-5 place-items-center rounded-md bg-brand-50 px-1 align-[1px] text-[11px] font-semibold text-brand-700 transition hover:bg-brand-500 hover:text-white dark:bg-brand-500/20 dark:text-brand-100">
                            {children}
                          </button>
                        );
                      },
                    }}>
                    {answerMd}
                  </ReactMarkdown>
                </div>
                {result.warnings.filter((w) => !MODEL_WARNING.test(w)).map((w) => (
                  <div key={w} className="mt-4 flex items-start gap-2 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-900 dark:bg-amber-500/10 dark:text-amber-200">
                    <AlertTriangle size={14} className="mt-0.5 shrink-0" /> {w}
                  </div>
                ))}
              </Card>
            ) : (
              <Card>
                <div className="flex items-start gap-3">
                  <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-500/15 dark:text-amber-300">
                    <ShieldAlert size={18} />
                  </div>
                  <div>
                    <h2 className="font-semibold">Sem evidências suficientes</h2>
                    <p className="mt-1 text-[15px] text-[var(--ink-2)]">{result.question}</p>
                    <p className="mt-3 text-sm">
                      {result.refusal_stage === "recuperacao"
                        ? "Recusada na recuperação — o LLM nem foi chamado, então não há o que alucinar."
                        : "Recusada na geração — o modelo avaliou que as avaliações recuperadas não sustentam uma resposta."}
                    </p>
                    {result.refusal_reason && <p className="mt-1 text-sm text-[var(--muted)]">{result.refusal_reason}</p>}
                  </div>
                </div>
              </Card>
            )}

            {result.evidences.length > 0 && (
              <Card title={`Evidências (${result.evidences.length})`}
                subtitle={`${cited.size} citadas na resposta · clique num número da resposta para ir à avaliação`}
                action={cited.size > 0 && (
                  <label className="flex cursor-pointer items-center gap-2 text-xs text-[var(--ink-2)]">
                    <input type="checkbox" checked={onlyCited} onChange={(e) => setOnlyCited(e.target.checked)} className="accent-[var(--series-1)]" />
                    Só citadas
                  </label>
                )}>
                <div className="grid gap-3">
                  {evidences.map((ev) => <EvidenceCard key={ev.ref} ev={ev} cited={cited.has(ev.ref)} active={activeRef === ev.ref} />)}
                </div>
              </Card>
            )}
          </div>
          <div className="lg:sticky lg:top-20"><Trace result={result} /></div>
        </div>
      )}
    </div>
  );
}
