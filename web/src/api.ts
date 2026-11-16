// Tipos e chamadas da API FastAPI (src/voc_rag/api.py).

export type Filters = {
  review_score?: { gte: number; lte: number };
  ano?: number;
  categoria?: string;
  entrega_status?: string[];
  uf?: string;
};

export type ModelStatus = {
  modelo: string;
  estado: "disponivel" | "sem_cota" | "erro";
  erro: string | null;
  desde: number | null; // epoch (s) da última falha
  principal: boolean;
};

export type Meta = {
  documentos: number;
  embeddings: string;
  provedor: string;
  modelo: string | null;
  modelos: ModelStatus[];
  limiar: number;
  top_k: number;
  categorias: string[];
  ufs: string[];
  anos: number[];
  entrega: { valor: string; rotulo: string }[];
  exemplos: string[];
};

export type Evidence = {
  ref: number;
  review_id: string;
  texto: string;
  review_score: number;
  data_compra: string;
  categoria: string;
  uf: string;
  entrega_status: string;
  dias_atraso: number | null;
  temas: string[];
  similarity: number;
  dense_rank: number | null;
  bm25_rank: number | null;
};

export type Theme = { tema: string; rotulo: string; n: number; pct: number };

export type AskResult = {
  question: string;
  status: "ok" | "sem_evidencia";
  answer: string;
  refusal_stage: "recuperacao" | "geracao" | null;
  refusal_reason: string | null;
  parsed: { search_text: string; notes: string[]; broad: boolean };
  filters: Filters;
  evidences: Evidence[];
  cited_refs: number[];
  retrieval: {
    min_similarity: number;
    max_similarity: number;
    support_similarity: number;
    n_dense: number;
    n_bm25: number;
    n_candidates: number;
    n_above_threshold: number;
    queries: string[];
    stats: { total?: number; nota_media?: number; temas?: Theme[] };
  };
  context: string | null;
  warnings: string[];
  provider: string;
  model: string;
  requested_model: string;
  timings_ms: Record<string, number>;
};

export type BaseMetrics = {
  total: number;
  nota_media: number;
  pct_negativas: number;
  pct_atraso: number;
  periodo: [string, string];
  por_nota: { nota: number; avaliacoes: number }[];
  por_mes: { mes: string; avaliacoes: number; nota_media: number; pct_negativas: number }[];
  temas: { tema: string; rotulo: string; avaliacoes: number; pct: number; negativo: boolean }[];
  por_categoria: { categoria: string; avaliacoes: number; nota_media: number; pct_atraso: number }[];
  por_entrega: { status: string; rotulo: string; avaliacoes: number; nota_media: number }[];
  por_uf: { uf: string; avaliacoes: number; nota_media: number }[];
};

export type UsageRecord = {
  ts: string;
  pergunta: string;
  status: string;
  etapa_recusa: string | null;
  citacoes: number;
  evidencias: number;
  ms_total: number;
  provedor: string;
  modelo: string;
  fallback: boolean;
};

export type UsageMetrics = {
  total: number;
  respondidas?: number;
  recusadas_recuperacao?: number;
  recusadas_geracao?: number;
  chamadas_llm?: number;
  fallbacks?: number;
  trocas_de_modelo?: number;
  por_modelo?: { modelo: string; respostas: number }[];
  citacoes_media?: number;
  ms_mediana_total?: number;
  ms_mediana_geracao?: number;
  por_dia?: { dia: string; respondidas: number; recusadas: number }[];
  registros: UsageRecord[];
};

export type QualityMetrics = {
  gerado_em: string;
  recuperacao: {
    backend: string;
    perguntas: number;
    filtros_corretos: string;
    relevancia_termos_media: number | null;
    limiar_sugerido: number;
    acuracia_escopo_limiar_sugerido: number;
    sim_suporte_no_escopo_min: number;
    sim_suporte_fora_escopo_max: number;
    linhas: {
      pergunta: string;
      no_escopo: boolean;
      filtros_ok: boolean;
      relevancia_termos: number | null;
      sim_max: number;
      sim_suporte: number;
    }[];
  };
  ponta_a_ponta: {
    provedor: string;
    modelo: string;
    limiar: number;
    corretas: number;
    perguntas: number;
    linhas: {
      pergunta: string;
      tipo: string;
      esperado: string;
      obtido: string;
      etapa_recusa: string | null;
      citacoes: number;
      correto: boolean;
    }[];
  } | null;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* corpo não é JSON */
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  meta: () => request<Meta>("/api/meta"),
  ask: (question: string, filters: Filters, top_k?: number, model?: string | null) =>
    request<AskResult>("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, filters, top_k, model: model || undefined }),
    }),
  models: () => request<ModelStatus[]>("/api/models"),
  base: () => request<BaseMetrics>("/api/dashboard/base"),
  usage: () => request<UsageMetrics>("/api/dashboard/uso"),
  quality: () => request<QualityMetrics>("/api/dashboard/qualidade"),
};

export const fmt = {
  int: (n: number) => n.toLocaleString("pt-BR"),
  dec: (n: number, digits = 2) => n.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits }),
  pct: (n: number, digits = 1) => `${n.toLocaleString("pt-BR", { maximumFractionDigits: digits })}%`,
  ms: (n: number) => (n >= 1000 ? `${(n / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} s` : `${n} ms`),
  category: (c: string) => c.replace(/_/g, " "),
  time: (epochS: number) => new Date(epochS * 1000).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
};
