"""Métricas do dashboard: base de avaliações, uso do RAG e qualidade (avaliação)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .themes import THEME_LABELS

DELIVERY_LABELS = {"no_prazo": "No prazo", "atrasada": "Atrasada", "nao_entregue": "Sem entrega registrada"}
NEGATIVE_THEMES = {
    "entrega_atrasada", "produto_nao_recebido", "entrega_incompleta", "produto_com_defeito",
    "produto_errado", "qualidade_baixa", "atendimento", "devolucao_reembolso",
}


# ----------------------------------------------------------------- base de avaliações
def base_metrics(docs: pd.DataFrame, min_category_reviews: int = 300) -> dict:
    """Agregados sobre as avaliações indexadas (calculados uma vez e mantidos em memória)."""
    total = len(docs)
    scores = docs["review_score"].value_counts().sort_index()

    monthly = (
        docs.groupby("ano_mes")
        .agg(avaliacoes=("review_id", "size"), nota_media=("review_score", "mean"),
             negativas=("review_score", lambda s: (s <= 2).mean()))
        .reset_index()
    )
    # meses com poucas avaliações (início e fim da série) distorcem a média
    monthly = monthly[monthly["avaliacoes"] >= 100]

    themes = docs["temas"].str.split("|").explode()
    themes = themes[themes.astype(bool)]
    theme_counts = themes.value_counts()

    by_category = (
        docs.groupby("categoria")
        .agg(avaliacoes=("review_id", "size"), nota_media=("review_score", "mean"),
             atrasadas=("entrega_status", lambda s: (s != "no_prazo").mean()))
        .reset_index()
    )
    by_category = by_category[
        (by_category["avaliacoes"] >= min_category_reviews) & (by_category["categoria"] != "desconhecida")
    ].sort_values("nota_media")

    by_delivery = (
        docs.groupby("entrega_status")
        .agg(avaliacoes=("review_id", "size"), nota_media=("review_score", "mean"))
        .reset_index()
    )
    by_state = (
        docs.groupby("uf").agg(avaliacoes=("review_id", "size"), nota_media=("review_score", "mean"))
        .reset_index().sort_values("avaliacoes", ascending=False).head(10)
    )

    return {
        "total": total,
        "nota_media": round(float(docs["review_score"].mean()), 2),
        "pct_negativas": round(float((docs["review_score"] <= 2).mean()) * 100, 1),
        "pct_atraso": round(float((docs["entrega_status"] != "no_prazo").mean()) * 100, 1),
        "periodo": [str(docs["ano_mes"].min()), str(docs["ano_mes"].max())],
        "por_nota": [{"nota": int(k), "avaliacoes": int(v)} for k, v in scores.items()],
        "por_mes": [
            {"mes": r.ano_mes, "avaliacoes": int(r.avaliacoes), "nota_media": round(float(r.nota_media), 2),
             "pct_negativas": round(float(r.negativas) * 100, 1)}
            for r in monthly.itertuples()
        ],
        "temas": [
            {"tema": t, "rotulo": THEME_LABELS.get(t, t), "avaliacoes": int(n),
             "pct": round(n / total * 100, 1), "negativo": t in NEGATIVE_THEMES}
            for t, n in theme_counts.items()
        ],
        "por_categoria": [
            {"categoria": r.categoria, "avaliacoes": int(r.avaliacoes),
             "nota_media": round(float(r.nota_media), 2), "pct_atraso": round(float(r.atrasadas) * 100, 1)}
            for r in by_category.itertuples()
        ],
        "por_entrega": [
            {"status": r.entrega_status, "rotulo": DELIVERY_LABELS.get(r.entrega_status, r.entrega_status),
             "avaliacoes": int(r.avaliacoes), "nota_media": round(float(r.nota_media), 2)}
            for r in by_delivery.itertuples()
        ],
        "por_uf": [
            {"uf": r.uf, "avaliacoes": int(r.avaliacoes), "nota_media": round(float(r.nota_media), 2)}
            for r in by_state.itertuples()
        ],
    }


# ----------------------------------------------------------------- uso do RAG
def log_query(path: Path, result, manual_filters: dict | None) -> None:
    """Uma linha JSON por pergunta feita na interface (arquivo local, fora do git)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    timings = result.timings_ms or {}
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pergunta": result.question,
        "status": result.status,
        "etapa_recusa": result.refusal_stage,
        "filtros": result.filters,
        "filtros_manuais": bool(manual_filters),
        "evidencias": len(result.evidences),
        "citacoes": len(result.cited_refs),
        "sim_max": round(result.retrieval.max_similarity, 3),
        "sim_suporte": round(result.retrieval.support_similarity, 3),
        "provedor": result.provider or "nenhum",
        "modelo": result.model or "",
        "modelo_solicitado": result.requested_model or "",
        "troca_de_modelo": bool(result.requested_model and result.model not in ("", "nenhum", result.requested_model)),
        "fallback": result.provider == "extractive_fallback",
        "ms_total": int(sum(timings.values())),
        "ms_recuperacao": int(timings.get("recuperacao", 0)),
        "ms_geracao": int(timings.get("geracao", 0)),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def usage_metrics(path: Path, recent: int = 15) -> dict:
    records = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # linha truncada não derruba o dashboard
    total = len(records)
    if not total:
        return {"total": 0, "registros": []}

    answered = [r for r in records if r["status"] == "ok"]
    generated = [r for r in records if r["ms_geracao"]]
    by_day: dict[str, dict] = {}
    for r in records:
        day = by_day.setdefault(r["ts"][:10], {"dia": r["ts"][:10], "respondidas": 0, "recusadas": 0})
        day["respondidas" if r["status"] == "ok" else "recusadas"] += 1

    def median(values: list[int]) -> int:
        values = sorted(values)
        return values[len(values) // 2] if values else 0

    return {
        "total": total,
        "respondidas": len(answered),
        "recusadas_recuperacao": sum(r["etapa_recusa"] == "recuperacao" for r in records),
        "recusadas_geracao": sum(r["etapa_recusa"] == "geracao" for r in records),
        "chamadas_llm": sum(1 for r in generated if not r.get("fallback")),
        "fallbacks": sum(1 for r in records if r.get("fallback")),
        "trocas_de_modelo": sum(1 for r in records if r.get("troca_de_modelo")),
        "por_modelo": _count_models(records),
        "citacoes_media": round(sum(r["citacoes"] for r in answered) / len(answered), 1) if answered else 0,
        "ms_mediana_total": median([r["ms_total"] for r in records]),
        "ms_mediana_geracao": median([r["ms_geracao"] for r in generated]),
        "por_dia": sorted(by_day.values(), key=lambda d: d["dia"]),
        "registros": list(reversed(records[-recent:])),
    }


def _count_models(records: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for r in records:
        if r.get("ms_geracao") and r.get("modelo") not in (None, "", "nenhum"):
            counts[r["modelo"]] = counts.get(r["modelo"], 0) + 1
    return [{"modelo": m, "respostas": n} for m, n in sorted(counts.items(), key=lambda kv: -kv[1])]


# ----------------------------------------------------------------- qualidade
def quality_metrics(path: Path) -> dict | None:
    """Resultado estruturado de `python -m voc_rag.cli eval` (eval/resultado.json)."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
