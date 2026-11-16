"""Etapa 4 — recuperação híbrida, seleção e verificação de suficiência das evidências.

Fluxo: busca densa (Chroma) + busca lexical (BM25) → fusão por RRF → corte por
similaridade mínima → diversificação por MMR → top-k.

- Densa: encontra paráfrases ("não chegou" ~ "até agora nada do produto").
- BM25: garante termos exatos que o embedding dilui (nomes de produto, "nota fiscal").
- RRF: combina os dois rankings sem precisar normalizar escalas de score diferentes.
- Perguntas amplas ("quais os principais problemas?") não têm um assunto para buscar: a
  palavra "problemas" só encontraria quem escreveu "problemas". Nesses casos a busca é
  decomposta em sub-buscas, uma para cada tema mais frequente do recorte filtrado
  (decomposição guiada pelos dados), e os rankings são fundidos pelo mesmo RRF.
- MMR: a base tem milhares de comentários quase idênticos ("não recebi o produto");
  sem diversificar, o contexto viraria 12 cópias da mesma frase.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

from .config import DEFAULT_MIN_SIMILARITY, Settings
from .embeddings import load_embedder
from .index import open_collection, read_manifest
from .query import Filters, ParsedQuery, to_chroma_where, to_mask
from .text import tokenize
from .themes import POSITIVE_THEMES, THEME_LABELS, THEME_QUERIES

RRF_K = 60


@dataclass
class Evidence:
    ref: int  # número usado nas citações [n]
    review_id: str
    texto: str
    review_score: int
    data_compra: str
    categoria: str
    uf: str
    entrega_status: str
    dias_atraso: int | None
    temas: list[str]
    similarity: float
    dense_rank: int | None
    bm25_rank: int | None
    rrf_score: float


@dataclass
class RetrievalResult:
    evidences: list[Evidence]
    sufficient: bool
    reason: str
    min_similarity: float
    max_similarity: float
    # similaridade da N-ésima melhor avaliação distinta (N = MIN_EVIDENCES): é o número
    # comparado com o limiar para decidir se há evidência suficiente
    support_similarity: float
    n_dense: int
    n_bm25: int
    n_candidates: int
    n_above_threshold: int
    stats: dict = field(default_factory=dict)
    queries: list[str] = field(default_factory=list)  # textos efetivamente buscados


MAX_SUBQUERIES = 5


class Retriever:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.manifest = read_manifest(settings)
        self.docs = pd.read_parquet(settings.documents_path).set_index("review_id", drop=False)
        self.collection = open_collection(settings.index_dir)
        self.embedder = load_embedder(
            self.manifest["embedding_backend"], settings.embedding_model, settings.index_dir
        )
        self._ids = self.docs["review_id"].to_numpy()
        self._bm25 = BM25Okapi([tokenize(t) for t in self.docs["texto"]])
        self.categories = sorted(self.docs["categoria"].unique().tolist())
        self.min_similarity = (
            settings.min_similarity
            if settings.min_similarity is not None
            else self.manifest.get(
                "min_similarity", DEFAULT_MIN_SIMILARITY[self.manifest["embedding_backend"]]
            )
        )

    # ------------------------------------------------------------------ buscas
    def _dense(self, query_vector: np.ndarray, filters: Filters) -> list[str]:
        result = self.collection.query(
            query_embeddings=[query_vector],
            n_results=self.settings.dense_candidates,
            where=to_chroma_where(filters),
            include=[],
        )
        return result["ids"][0]

    def _lexical(self, search_text: str, mask: np.ndarray) -> list[str]:
        tokens = tokenize(search_text)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        scores[~mask] = 0.0
        top = np.argsort(-scores)[: self.settings.bm25_candidates]
        return [self._ids[i] for i in top if scores[i] > 0]

    def _vectors(self, ids: list[str]) -> dict[str, np.ndarray]:
        got = self.collection.get(ids=ids, include=["embeddings"])
        return {rid: np.asarray(vec, dtype=np.float32) for rid, vec in zip(got["ids"], got["embeddings"])}

    # ------------------------------------------------------------------ seleção
    def _mmr(self, ordered: list[str], relevance: dict[str, float], vectors: dict, k: int) -> list[str]:
        """Maximal Marginal Relevance sobre os candidatos já fundidos."""
        top = max(relevance.values())
        selected: list[str] = []
        pool = list(ordered)
        while pool and len(selected) < k:
            best_id, best_score = pool[0], -np.inf
            for rid in pool:
                redundancy = max((float(vectors[rid] @ vectors[s]) for s in selected), default=0.0)
                score = (
                    self.settings.mmr_lambda * relevance[rid] / top
                    - (1 - self.settings.mmr_lambda) * redundancy
                )
                if score > best_score:
                    best_id, best_score = rid, score
            selected.append(best_id)
            pool.remove(best_id)
        return selected

    def _stats(self, mask: np.ndarray) -> dict:
        """Panorama quantitativo do recorte filtrado (base inteira se não houver filtro)."""
        subset = self.docs[mask]
        total = int(len(subset))
        if total == 0:
            return {"total": 0}
        themes = subset["temas"].str.split("|").explode()
        counts = themes[themes != ""].value_counts()
        return {
            "total": total,
            "nota_media": round(float(subset["review_score"].mean()), 2),
            "por_nota": {int(k): int(v) for k, v in subset["review_score"].value_counts().sort_index().items()},
            "temas": [
                {"tema": name, "rotulo": THEME_LABELS[name], "n": int(n), "pct": round(100 * n / total, 1)}
                for name, n in counts.items()
            ],
        }

    def _expand(self, parsed: ParsedQuery, filters: Filters, stats: dict) -> list[str]:
        """Textos de busca: o da pergunta ou, se ela for ampla, um por tema frequente."""
        if not parsed.broad:
            return [parsed.search_text]
        score = filters.get("review_score") if isinstance(filters.get("review_score"), dict) else {}
        themes = [t["tema"] for t in stats.get("temas", [])]
        if score.get("lte", 5) <= 3:  # pergunta sobre problemas: temas positivos não entram
            themes = [t for t in themes if t not in POSITIVE_THEMES]
        elif score.get("gte", 1) >= 4:  # pergunta sobre elogios
            themes = [t for t in themes if t in POSITIVE_THEMES]
        queries = [THEME_QUERIES[t] for t in themes[:MAX_SUBQUERIES]]
        return queries or [parsed.search_text]

    # ------------------------------------------------------------------ API
    def retrieve(self, parsed: ParsedQuery, filters: Filters | None = None, k: int | None = None) -> RetrievalResult:
        filters = parsed.filters if filters is None else filters
        k = k or self.settings.top_k
        mask = to_mask(filters, self.docs)
        stats = self._stats(mask)

        def empty(reason: str, **extra) -> RetrievalResult:
            base = dict(max_similarity=0.0, support_similarity=0.0, n_dense=0, n_bm25=0, n_candidates=0, n_above_threshold=0)
            base.update(extra)
            return RetrievalResult([], False, reason, self.min_similarity, stats=stats, **base)

        if stats["total"] == 0:
            return empty("Nenhuma avaliação na base atende aos filtros aplicados.")

        queries = self._expand(parsed, filters, stats)
        query_vectors = [self.embedder.embed_query(q) for q in queries]
        dense_lists = [self._dense(vec, filters) for vec in query_vectors]
        bm25_lists = [self._lexical(q, mask) for q in queries]

        # Reciprocal Rank Fusion sobre todos os rankings (denso e lexical de cada busca)
        rrf: dict[str, float] = {}
        dense_rank: dict[str, int] = {}
        bm25_rank: dict[str, int] = {}
        for ranking, best in [(l, dense_rank) for l in dense_lists] + [(l, bm25_rank) for l in bm25_lists]:
            for position, rid in enumerate(ranking, start=1):
                rrf[rid] = rrf.get(rid, 0.0) + 1.0 / (RRF_K + position)
                best[rid] = min(best.get(rid, position), position)
        if not rrf:
            return empty("A busca não retornou nenhum candidato.", queries=queries)

        vectors = self._vectors(list(rrf))
        # similaridade com a busca mais próxima (há mais de uma só em perguntas amplas)
        sims = {rid: max(float(vectors[rid] @ qv) for qv in query_vectors) for rid in rrf}
        max_sim = max(sims.values())
        counts = dict(n_dense=len(dense_rank), n_bm25=len(bm25_rank), n_candidates=len(rrf), queries=queries)

        # Textos idênticos contam uma vez só como evidência
        seen: set[str] = set()
        unique = []
        for rid in sorted(rrf, key=rrf.get, reverse=True):
            key = self.docs.at[rid, "texto_norm"]
            if key not in seen:
                seen.add(key)
                unique.append(rid)

        need = self.settings.min_evidences
        top_sims = sorted((sims[rid] for rid in unique), reverse=True)
        support_sim = top_sims[need - 1] if len(top_sims) >= need else 0.0
        counts["support_similarity"] = support_sim

        # Corte de relevância: todo candidato (inclusive os que vieram só do BM25) precisa
        # de similaridade semântica mínima com a pergunta. É a 1ª barreira anti-alucinação.
        relevant = [rid for rid in unique if sims[rid] >= self.min_similarity]

        if len(relevant) < need:
            return empty(
                f"Apenas {len(relevant)} avaliação(ões) atingiram a similaridade mínima de "
                f"{self.min_similarity:.2f} (maior similaridade encontrada: {max_sim:.2f}; "
                f"mínimo exigido: {need} avaliações).",
                max_similarity=max_sim,
                n_above_threshold=len(relevant),
                **counts,
            )

        chosen = self._mmr(relevant, rrf, vectors, k)
        evidences = []
        for ref, rid in enumerate(chosen, start=1):
            row = self.docs.loc[rid]
            evidences.append(
                Evidence(
                    ref=ref,
                    review_id=rid,
                    texto=row["texto"],
                    review_score=int(row["review_score"]),
                    data_compra=row["data_compra"],
                    categoria=row["categoria"],
                    uf=row["uf"],
                    entrega_status=row["entrega_status"],
                    dias_atraso=None if pd.isna(row["dias_atraso"]) else int(row["dias_atraso"]),
                    temas=[t for t in row["temas"].split("|") if t],
                    similarity=round(sims[rid], 4),
                    dense_rank=dense_rank.get(rid),
                    bm25_rank=bm25_rank.get(rid),
                    rrf_score=round(rrf[rid], 5),
                )
            )
        return RetrievalResult(
            evidences, True, "ok", self.min_similarity, max_sim, n_above_threshold=len(relevant), stats=stats, **counts
        )
