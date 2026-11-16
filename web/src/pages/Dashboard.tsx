import { ReactNode, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Bar, BarChart, CartesianGrid, Cell, LabelList, Line, LineChart, ReferenceLine, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { CheckCircle2, RefreshCw, XCircle } from "lucide-react";
import { api, BaseMetrics, fmt, QualityMetrics, UsageMetrics } from "../api";
import { Card, LegendDot, Pill, Skeleton, Stat } from "../components/ui";

// SVG não resolve var() em atributos de forma confiável: lemos os papéis de cor
// calculados (claro/escuro definidos em index.css) e passamos o hex aos gráficos.
type Palette = { s1: string; s2: string; neg: string; grid: string; axis: string; ink2: string; surface: string; muted: string };

function readPalette(): Palette {
  const css = getComputedStyle(document.documentElement);
  const v = (name: string) => css.getPropertyValue(name).trim();
  return {
    s1: v("--series-1"), s2: v("--series-2"), neg: v("--series-neg"), grid: v("--grid"),
    axis: v("--axis"), ink2: v("--ink-2"), surface: v("--surface"), muted: v("--muted"),
  };
}

function usePalette(): Palette {
  const [palette, setPalette] = useState(readPalette);
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const update = () => setPalette(readPalette());
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  return palette;
}

function chartBits(C: Palette) {
  return {
    axisProps: { stroke: C.axis, tickLine: false, axisLine: { stroke: C.axis }, tick: { fill: C.muted, fontSize: 12 } },
    cursor: { fill: C.grid, opacity: 0.5 },
    label: { fill: C.ink2, fontSize: 12 },
  };
}

type Tab = "base" | "uso" | "qualidade";

function useLoad<T>(loader: () => Promise<T>, key: unknown) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    setData(null); setError(null);
    loader().then(setData).catch((e: Error) => setError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return { data, error };
}

function Loading() {
  return (
    <div className="grid gap-4">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />)}</div>
      <div className="grid gap-4 lg:grid-cols-2"><Skeleton className="h-72" /><Skeleton className="h-72" /></div>
    </div>
  );
}

function ErrorBox({ children }: { children: ReactNode }) {
  return <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-200">{children}</div>;
}

// ------------------------------------------------------------------ base de avaliações
function BaseTab() {
  const C = usePalette();
  const { axisProps, cursor, label } = chartBits(C);
  const { data, error } = useLoad<BaseMetrics>(api.base, "base");
  if (error) return <ErrorBox>{error}</ErrorBox>;
  if (!data) return <Loading />;

  // 6 piores e 4 melhores categorias, como diferença para a nota média geral
  const ranked = data.por_categoria;
  const extremes = [...ranked.slice(0, 6), ...ranked.slice(-4)]
    .map((c) => ({ ...c, delta: Math.round((c.nota_media - data.nota_media) * 100) / 100 }));
  const span = Math.ceil(Math.max(...extremes.map((c) => Math.abs(c.delta))) * 10) / 10;
  const signed = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${fmt.dec(Math.abs(v))}`;
  const themes = data.temas.slice(0, 10);
  const delivery = [...data.por_entrega].sort((a, b) => b.nota_media - a.nota_media);
  const monthLabel = (m: string) => { const [y, mo] = m.split("-"); return `${mo}/${y.slice(2)}`; };

  return (
    <div className="grid gap-4">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Avaliações com texto" value={fmt.int(data.total)} hint={`${monthLabel(data.periodo[0])} a ${monthLabel(data.periodo[1])}`} />
        <Stat label="Nota média" value={fmt.dec(data.nota_media)} hint="escala de 1 a 5" />
        <Stat label="Avaliações negativas" value={fmt.pct(data.pct_negativas)} hint="nota 1 ou 2" />
        <Stat label="Pedidos com problema de entrega" value={fmt.pct(data.pct_atraso)} hint="atrasados ou sem entrega registrada" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Entrega é o que mais derruba a nota"
          subtitle="Nota média por situação real da entrega (datas do pedido, não o texto)">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={delivery} layout="vertical" margin={{ left: 8, right: 48 }}>
              <CartesianGrid horizontal={false} stroke={C.grid} />
              <XAxis type="number" domain={[0, 5]} ticks={[0, 1, 2, 3, 4, 5]} {...axisProps} />
              <YAxis type="category" dataKey="rotulo" width={150} {...axisProps} axisLine={false} />
              <Tooltip cursor={cursor} formatter={(v: number, _n, p) => [`${fmt.dec(v)} · ${fmt.int(p.payload.avaliacoes)} avaliações`, "Nota média"]} />
              <Bar isAnimationActive={false} dataKey="nota_media" fill={C.s1} radius={[0, 4, 4, 0]} barSize={22}>
                <LabelList dataKey="nota_media" position="right" formatter={(v: number) => fmt.dec(v)} {...label} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {delivery.length === 3 && (
            <p className="mt-3 rounded-lg bg-black/[0.03] px-3 py-2 text-sm text-[var(--ink-2)] dark:bg-white/5">
              Pedidos atrasados têm nota média <strong className="text-[var(--ink)]">{fmt.dec(delivery[0].nota_media - delivery[1].nota_media)} pontos menor</strong> que os entregues no prazo
              ({fmt.int(delivery[1].avaliacoes + delivery[2].avaliacoes)} avaliações afetadas por atraso ou falta de entrega).
            </p>
          )}
        </Card>

        <Card title="Temas mais citados" subtitle="Avaliações por tema (palavras-chave; uma avaliação pode ter vários)"
          action={<div className="flex gap-3"><LegendDot color={C.neg} label="Problema" /><LegendDot color={C.s1} label="Elogio" /></div>}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={themes} layout="vertical" margin={{ left: 8, right: 56 }}>
              <CartesianGrid horizontal={false} stroke={C.grid} />
              <XAxis type="number" {...axisProps} tickFormatter={(v) => fmt.int(v)} />
              <YAxis type="category" dataKey="rotulo" width={190} {...axisProps} axisLine={false} tick={{ fill: C.muted, fontSize: 12 }} />
              <Tooltip cursor={cursor} formatter={(v: number, _n, p) => [`${fmt.int(v)} (${fmt.pct(p.payload.pct)})`, "Avaliações"]} />
              <Bar isAnimationActive={false} dataKey="avaliacoes" radius={[0, 4, 4, 0]} barSize={16}>
                {themes.map((t) => <Cell key={t.tema} fill={t.negativo ? C.neg : C.s1} />)}
                <LabelList dataKey="pct" position="right" formatter={(v: number) => fmt.pct(v)} {...label} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Volume de avaliações por mês" subtitle="Meses com 100 ou mais avaliações">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.por_mes} margin={{ left: -8, right: 8 }}>
              <CartesianGrid vertical={false} stroke={C.grid} />
              <XAxis dataKey="mes" tickFormatter={monthLabel} {...axisProps} interval="preserveStartEnd" minTickGap={16} />
              <YAxis {...axisProps} axisLine={false} tickFormatter={(v) => fmt.int(v)} />
              <Tooltip cursor={cursor} labelFormatter={monthLabel} formatter={(v: number) => [fmt.int(v), "Avaliações"]} />
              <Bar isAnimationActive={false} dataKey="avaliacoes" fill={C.s1} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Avaliações negativas ao longo do tempo" subtitle="% de notas 1 ou 2 no mês">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.por_mes} margin={{ left: -8, right: 8 }}>
              <CartesianGrid vertical={false} stroke={C.grid} />
              <XAxis dataKey="mes" tickFormatter={monthLabel} {...axisProps} interval="preserveStartEnd" minTickGap={16} />
              <YAxis {...axisProps} axisLine={false} tickFormatter={(v) => `${v}%`} domain={[0, "auto"]} />
              <Tooltip labelFormatter={monthLabel} formatter={(v: number) => [fmt.pct(v), "Negativas"]} />
              <ReferenceLine y={data.pct_negativas} stroke={C.axis} strokeDasharray="4 4"
                label={{ value: `média ${fmt.pct(data.pct_negativas)}`, position: "insideTopRight", fill: C.muted, fontSize: 11 }} />
              <Line isAnimationActive={false} dataKey="pct_negativas" stroke={C.neg} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
        <Card title="Categorias que mais se afastam da média"
          subtitle={`Diferença da nota média para a média geral (${fmt.dec(data.nota_media)}) · categorias com 300 ou mais avaliações`}
          action={<div className="flex gap-3"><LegendDot color={C.neg} label="Abaixo" /><LegendDot color={C.s1} label="Acima" /></div>}>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={extremes} layout="vertical" margin={{ left: 8, right: 52 }}>
              <CartesianGrid horizontal={false} stroke={C.grid} />
              <XAxis type="number" domain={[-(span + 0.2), span + 0.2]} tickFormatter={signed} {...axisProps} />
              <YAxis type="category" dataKey="categoria" width={170} tickFormatter={fmt.category} {...axisProps} axisLine={false} tick={{ fill: C.muted, fontSize: 12 }} />
              <Tooltip cursor={cursor} labelFormatter={fmt.category}
                formatter={(_v: number, _n, p) => [`${fmt.dec(p.payload.nota_media)} (${signed(p.payload.delta)}) · ${fmt.int(p.payload.avaliacoes)} avaliações · ${fmt.pct(p.payload.pct_atraso)} com problema de entrega`, "Nota média"]} />
              <ReferenceLine x={0} stroke={C.axis} />
              <Bar isAnimationActive={false} dataKey="delta" radius={4} barSize={16}>
                {extremes.map((c) => <Cell key={c.categoria} fill={c.delta < 0 ? C.neg : C.s1} />)}
                <LabelList dataKey="delta" position="right" formatter={signed} {...label} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Distribuição das notas" subtitle="Avaliações por nota">
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={data.por_nota} margin={{ left: -8, right: 8 }}>
              <CartesianGrid vertical={false} stroke={C.grid} />
              <XAxis dataKey="nota" {...axisProps} tickFormatter={(v) => `${v}★`} />
              <YAxis {...axisProps} axisLine={false} tickFormatter={(v) => fmt.int(v)} />
              <Tooltip cursor={cursor} labelFormatter={(v) => `Nota ${v}`} formatter={(v: number) => [`${fmt.int(v)} (${fmt.pct((v / data.total) * 100)})`, "Avaliações"]} />
              <Bar isAnimationActive={false} dataKey="avaliacoes" fill={C.s1} radius={[4, 4, 0, 0]} barSize={36} />
            </BarChart>
          </ResponsiveContainer>
          <h3 className="mb-2 mt-5 text-sm font-semibold">Estados com mais avaliações</h3>
          <table className="w-full text-sm tabular">
            <thead><tr className="text-left text-xs text-[var(--muted)]"><th className="pb-1.5 font-medium">UF</th><th className="pb-1.5 text-right font-medium">Avaliações</th><th className="pb-1.5 text-right font-medium">Nota média</th></tr></thead>
            <tbody>
              {data.por_uf.slice(0, 6).map((u) => (
                <tr key={u.uf} className="border-t border-black/5 dark:border-white/10">
                  <td className="py-1.5">{u.uf}</td><td className="py-1.5 text-right">{fmt.int(u.avaliacoes)}</td><td className="py-1.5 text-right">{fmt.dec(u.nota_media)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ uso do RAG
function UsageTab({ refresh }: { refresh: number }) {
  const C = usePalette();
  const { axisProps, cursor } = chartBits(C);
  const { data, error } = useLoad<UsageMetrics>(api.usage, `uso-${refresh}`);
  if (error) return <ErrorBox>{error}</ErrorBox>;
  if (!data) return <Loading />;
  if (!data.total) return <ErrorBox>Nenhuma pergunta registrada ainda. Faça perguntas na aba Perguntar — cada uma é registrada em <code>data/logs/perguntas.jsonl</code>.</ErrorBox>;

  const refused = (data.recusadas_recuperacao ?? 0) + (data.recusadas_geracao ?? 0);
  return (
    <div className="grid gap-4">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Perguntas feitas" value={fmt.int(data.total)} hint={`${fmt.int(data.chamadas_llm ?? 0)} ${data.chamadas_llm === 1 ? "chamada" : "chamadas"} ao LLM`} />
        <Stat label="Respondidas" value={fmt.pct(((data.respondidas ?? 0) / data.total) * 100, 0)} hint={`${data.respondidas} com ${fmt.dec(data.citacoes_media ?? 0, 1)} citações em média`} />
        <Stat label="Recusadas" value={fmt.int(refused)}
          hint={`${data.recusadas_recuperacao} na recuperação (sem LLM) · ${data.recusadas_geracao} pelo LLM`} />
        <Stat label="Tempo de resposta" value={fmt.ms(data.ms_mediana_total ?? 0)} hint={`mediana · geração ${fmt.ms(data.ms_mediana_geracao ?? 0)}`} />
      </div>
      {(data.fallbacks ?? 0) > 0 && (
        <ErrorBox>{data.fallbacks} pergunta(s) caíram no modo extrativo porque o LLM estava indisponível (limite de requisições ou erro do provedor).</ErrorBox>
      )}
      <div className="grid gap-4 lg:grid-cols-[2fr_3fr]">
        <Card title="Perguntas por dia" action={<div className="flex gap-3"><LegendDot color={C.s1} label="Respondidas" /><LegendDot color={C.s2} label="Recusadas" /></div>}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.por_dia} margin={{ left: -16, right: 8 }}>
              <CartesianGrid vertical={false} stroke={C.grid} />
              <XAxis dataKey="dia" {...axisProps} tickFormatter={(d: string) => d.slice(5).split("-").reverse().join("/")} />
              <YAxis {...axisProps} axisLine={false} allowDecimals={false} />
              <Tooltip cursor={cursor} />
              <Bar isAnimationActive={false} dataKey="respondidas" name="Respondidas" stackId="a" fill={C.s1} />
              <Bar isAnimationActive={false} dataKey="recusadas" name="Recusadas" stackId="a" fill={C.s2} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Perguntas recentes">
          <div className="grid grid-cols-[minmax(0,1fr)] divide-y divide-black/5 dark:divide-white/10">
            {data.registros.map((r) => (
              <div key={r.ts + r.pergunta} className="flex items-center gap-3 py-2.5 text-sm">
                {r.status === "ok"
                  ? <CheckCircle2 size={16} className="shrink-0 text-[var(--good)]" aria-label="respondida" />
                  : <XCircle size={16} className="shrink-0 text-[var(--series-2)]" aria-label="recusada" />}
                <span className="min-w-0 flex-1 truncate" title={r.pergunta}>{r.pergunta}</span>
                {r.status === "ok"
                  ? <Pill tone="brand">{r.citacoes} citações</Pill>
                  : <Pill>{r.etapa_recusa === "recuperacao" ? "recusa: recuperação" : "recusa: LLM"}</Pill>}
                {r.fallback && <Pill tone="warn">sem LLM</Pill>}
                <span className="hidden w-14 shrink-0 text-right text-xs tabular text-[var(--muted)] sm:block">{fmt.ms(r.ms_total)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ qualidade
function QualityTab() {
  const C = usePalette();
  const { axisProps, cursor, label } = chartBits(C);
  const { data, error } = useLoad<QualityMetrics>(api.quality, "qualidade");
  if (error) return <ErrorBox>{error}</ErrorBox>;
  if (!data) return <Loading />;

  const ret = data.recuperacao;
  const e2e = data.ponta_a_ponta;
  const sorted = [...ret.linhas].sort((a, b) => a.sim_suporte - b.sim_suporte).map((r, i) => ({ ...r, y: i + 1 }));
  const inside = sorted.filter((r) => r.no_escopo);
  const outside = sorted.filter((r) => !r.no_escopo);
  const threshold = e2e?.limiar ?? ret.limiar_sugerido;
  const margin = ret.sim_suporte_no_escopo_min - ret.sim_suporte_fora_escopo_max;
  const relevance = ret.linhas.filter((r) => r.relevancia_termos !== null)
    .map((r) => ({ pergunta: r.pergunta, valor: r.relevancia_termos as number }))
    .sort((a, b) => a.valor - b.valor);
  const xs = sorted.map((r) => r.sim_suporte);

  return (
    <div className="grid gap-4">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {e2e && <Stat label="Decisão responder × recusar" value={`${e2e.corretas}/${e2e.perguntas}`}
          hint={`ponta a ponta · ${e2e.modelo || e2e.provedor}`} />}
        <Stat label="Filtros inferidos" value={ret.filtros_corretos} hint="corretos por pergunta" />
        <Stat label="Relevância@k" value={ret.relevancia_termos_media !== null ? fmt.dec(ret.relevancia_termos_media) : "—"} hint="média nas perguntas no escopo (por termos)" />
        <Stat label="Limiar de similaridade" value={fmt.dec(threshold, 3)} hint={`margem ${fmt.dec(margin, 3)} entre os grupos`} />
      </div>

      <Card title="Onde o limiar separa o que responder do que recusar"
        subtitle="Similaridade de suporte (3ª melhor avaliação) de cada pergunta de calibração. À direita da linha, o sistema responde."
        action={<div className="flex gap-3"><LegendDot color={C.s1} label="No escopo" /><LegendDot color={C.s2} label="Fora do escopo" /></div>}>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ left: -16, right: 16, top: 28 }}>
            <CartesianGrid stroke={C.grid} vertical={false} />
            <XAxis type="number" dataKey="sim_suporte" name="Suporte" domain={[Math.floor(Math.min(...xs) * 100) / 100, Math.ceil(Math.max(...xs) * 100) / 100]}
              tickFormatter={(v) => v.toFixed(2)} {...axisProps} />
            <YAxis type="number" dataKey="y" {...axisProps} tick={false} axisLine={false} width={24} />
            <ZAxis range={[70, 70]} />
            <Tooltip cursor={false} content={({ payload }) => {
              const p = payload?.[0]?.payload;
              if (!p) return null;
              return (
                <div className="max-w-xs rounded-lg border border-[var(--grid)] bg-[var(--surface)] px-3 py-2 text-xs shadow-lg">
                  <div className="font-semibold tabular">{p.sim_suporte.toFixed(3)}</div>
                  <div className="mt-0.5 text-[var(--ink-2)]">{p.pergunta}</div>
                </div>
              );
            }} />
            <ReferenceLine x={threshold} stroke={C.ink2} strokeDasharray="4 4"
              label={{ value: `limiar ${threshold.toFixed(3)}`, position: "top", fill: C.ink2, fontSize: 11 }} />
            <Scatter isAnimationActive={false} data={inside} fill={C.s1} stroke={C.surface} strokeWidth={2} />
            <Scatter isAnimationActive={false} data={outside} fill={C.s2} stroke={C.surface} strokeWidth={2} />
          </ScatterChart>
        </ResponsiveContainer>
        <p className="mt-2 text-xs text-[var(--muted)]">
          Menor suporte no escopo: {ret.sim_suporte_no_escopo_min.toFixed(3)} · maior fora do escopo: {ret.sim_suporte_fora_escopo_max.toFixed(3)}.
          A margem estreita é a principal fragilidade: perguntas novas podem cair do lado errado.
        </p>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Relevância@k por pergunta" subtitle="Fração das avaliações recuperadas que contêm um termo esperado">
          <ResponsiveContainer width="100%" height={Math.max(240, relevance.length * 28)}>
            <BarChart data={relevance} layout="vertical" margin={{ left: 0, right: 40 }}>
              <CartesianGrid horizontal={false} stroke={C.grid} />
              <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${v * 100}%`} {...axisProps} />
              <YAxis type="category" dataKey="pergunta" width={230} interval={0} {...axisProps} axisLine={false} tick={{ fill: C.muted, fontSize: 11 }}
                tickFormatter={(s: string) => (s.length > 38 ? s.slice(0, 37) + "…" : s)} />
              <Tooltip cursor={cursor} formatter={(v: number) => [fmt.pct(v * 100, 0), "Relevância@k"]} />
              <Bar isAnimationActive={false} dataKey="valor" fill={C.s1} radius={[0, 4, 4, 0]} barSize={12}>
                <LabelList dataKey="valor" position="right" formatter={(v: number) => fmt.pct(v * 100, 0)} {...label} fontSize={11} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
        {e2e && (
          <Card title="Teste ponta a ponta" subtitle={`${e2e.perguntas} perguntas com o pipeline completo`}>
            <div className="grid grid-cols-[minmax(0,1fr)] divide-y divide-black/5 dark:divide-white/10">
              {e2e.linhas.map((r) => (
                <div key={r.pergunta} className="flex items-center gap-3 py-2 text-sm">
                  {r.correto
                    ? <CheckCircle2 size={16} className="shrink-0 text-[var(--good)]" aria-label="correto" />
                    : <XCircle size={16} className="shrink-0 text-[var(--critical)]" aria-label="incorreto" />}
                  <span className="min-w-0 flex-1 truncate" title={r.pergunta}>{r.pergunta}</span>
                  <Pill tone={r.esperado === "responder" ? "brand" : "neutral"}>esperado: {r.esperado}</Pill>
                  {!r.correto && <Pill tone="bad">obtido: {r.obtido}</Pill>}
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
      <p className="text-xs text-[var(--muted)]">
        Fonte: <code>eval/resultado.json</code>, gerado em {new Date(data.gerado_em).toLocaleString("pt-BR")} por <code>python -m voc_rag.cli eval --write --e2e</code>.
      </p>
    </div>
  );
}

// ------------------------------------------------------------------ página
export default function DashboardPage() {
  const [params, setParams] = useSearchParams();
  const tab: Tab = (["base", "uso", "qualidade"] as Tab[]).includes(params.get("aba") as Tab) ? (params.get("aba") as Tab) : "base";
  const setTab = (t: Tab) => setParams(t === "base" ? {} : { aba: t }, { replace: true });
  const [refresh, setRefresh] = useState(0);
  const tabs: { id: Tab; label: string }[] = [
    { id: "base", label: "Base de avaliações" },
    { id: "uso", label: "Uso do RAG" },
    { id: "qualidade", label: "Qualidade" },
  ];
  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-[var(--ink-2)]">O que os clientes dizem, como o assistente está sendo usado e quão confiável ele é.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-xl border border-black/10 bg-[var(--surface)] p-1 dark:border-white/15">
            {tabs.map((t) => (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${tab === t.id
                  ? "bg-brand-500 text-white" : "text-[var(--ink-2)] hover:bg-black/5 dark:hover:bg-white/5"}`}>
                {t.label}
              </button>
            ))}
          </div>
          {tab === "uso" && (
            <button onClick={() => setRefresh((r) => r + 1)} title="Atualizar"
              className="grid h-9 w-9 place-items-center rounded-xl border border-black/10 bg-[var(--surface)] text-[var(--ink-2)] hover:text-[var(--ink)] dark:border-white/15">
              <RefreshCw size={15} />
            </button>
          )}
        </div>
      </div>
      {tab === "base" && <BaseTab />}
      {tab === "uso" && <UsageTab refresh={refresh} />}
      {tab === "qualidade" && <QualityTab />}
    </div>
  );
}
