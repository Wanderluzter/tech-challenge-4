"""Avaliação da recuperação e calibração do limiar de "evidência suficiente".

Mede, para cada pergunta de eval/perguntas.json:
- se os filtros inferidos batem com o esperado;
- relevância@k por termos: fração das evidências que contêm ao menos um termo esperado
  (proxy barato e auditável — não substitui julgamento humano de relevância);
- a similaridade de suporte (N-ésima melhor avaliação distinta), usada para escolher o
  limiar que separa perguntas no escopo das fora do escopo.
"""
from __future__ import annotations

import json
from pathlib import Path

from .config import Settings
from .index import write_manifest
from .query import parse_query
from .retriever import Retriever


def _best_threshold(inside: list[float], outside: list[float]) -> tuple[float, float]:
    """Limiar que maximiza a acurácia aceitar/recusar. Retorna (limiar, acurácia)."""
    if not outside or not inside:
        return 0.0, 1.0
    if max(outside) < min(inside):  # separável: ponto médio da margem
        return round((max(outside) + min(inside)) / 2, 3), 1.0
    best = (0.0, 0.0)
    for candidate in sorted({*inside, *outside}):
        hits = sum(s >= candidate for s in inside) + sum(s < candidate for s in outside)
        accuracy = hits / (len(inside) + len(outside))
        if accuracy > best[1]:
            best = (round(candidate, 3), accuracy)
    return best


FALLBACK = "extractive_fallback"


def ask_with_retry(pipeline, question: str, attempts: int = 4, wait_s: float = 30.0):
    """Pergunta ao pipeline repetindo quando o LLM falha (ex.: 429).

    Na interface, uma falha do LLM cai no modo extrativo; numa medição isso contaria como
    "respondida" sem o modelo ter decidido nada. Aqui a pergunta é refeita e, se o LLM
    continuar indisponível, o resultado volta marcado como fallback.
    """
    import sys
    import time

    # allow_fallback=False: uma medição usa um único modelo; trocar no meio misturaria resultados
    result = pipeline.ask(question, allow_fallback=False)
    for attempt in range(1, attempts):
        if result.provider != FALLBACK:
            break
        print(f"  LLM indisponível; nova tentativa em {wait_s:.0f}s ({attempt}/{attempts - 1})", file=sys.stderr)
        time.sleep(wait_s)
        result = pipeline.ask(question, allow_fallback=False)
    return result


def run_e2e(settings: Settings, questions_path: Path) -> dict:
    """Roda o pipeline completo (com o LLM configurado) e registra quem recusou o quê."""
    import sys

    from .pipeline import RagPipeline

    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    pipeline = RagPipeline(settings)
    rows = []
    for i, item in enumerate(questions, start=1):
        print(f"[{i}/{len(questions)}] {item['pergunta']}", file=sys.stderr)
        result = ask_with_retry(pipeline, item["pergunta"])
        failed = result.provider == FALLBACK
        expected = "responder" if item["no_escopo"] else "recusar"
        got = "erro_llm" if failed else ("responder" if result.status == "ok" else "recusar")
        rows.append(
            {
                "pergunta": item["pergunta"],
                "tipo": item.get("tipo") or ("no_escopo" if item["no_escopo"] else "fora_do_escopo"),
                "esperado": expected,
                "obtido": got,
                "etapa_recusa": result.refusal_stage,
                "citacoes": len(result.cited_refs),
                "correto": expected == got,
            }
        )
    model = pipeline.settings.llm_model if pipeline.generator.provider != "extractive" else ""
    return {
        "provedor": pipeline.generator.provider,
        "modelo": model,
        "limiar": pipeline.retriever.min_similarity,
        "corretas": sum(r["correto"] for r in rows),
        "perguntas": len(rows),
        "falhas_llm": sum(r["obtido"] == "erro_llm" for r in rows),
        "linhas": rows,
    }


def e2e_to_markdown(e2e: dict) -> str:
    model = f" / `{e2e['modelo']}`" if e2e["modelo"] else ""
    lines = [
        f"Ponta a ponta — geração: `{e2e['provedor']}`{model}, limiar {e2e['limiar']}",
        f"Decisão correta (responder x recusar): **{e2e['corretas']}/{e2e['perguntas']}**",
        "",
    ]
    if e2e.get("falhas_llm"):
        lines += [f"> Aviso: o LLM ficou indisponível em {e2e['falhas_llm']} pergunta(s) (`erro_llm`); "
                  "o resultado dessas perguntas não mede o sistema. Rode de novo.", ""]
    lines += [
        "| Pergunta | Esperado | Obtido | Etapa da recusa | Citações | Correto |",
        "|---|---|---|---|---|---|",
    ]
    for r in e2e["linhas"]:
        lines.append(
            f"| {r['pergunta']} | {r['esperado']} | {r['obtido']} | {r['etapa_recusa'] or '—'} | "
            f"{r['citacoes']} | {'✓' if r['correto'] else '✗'} |"
        )
    return "\n".join(lines) + "\n"


def run(settings: Settings, questions_path: Path, write: bool = False) -> dict:
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    # Perguntas do domínio mas sem resposta na base ("bateria do iPhone 15") recuperam
    # avaliações parecidas; quem deve recusá-las é o LLM, não o limiar. Ficam fora da calibração.
    questions = [q for q in questions if q.get("tipo") != "sem_resposta_na_base"]
    retriever = Retriever(settings)
    current = retriever.min_similarity
    retriever.min_similarity = -1.0  # desliga o corte para medir as similaridades cruas

    rows = []
    for item in questions:
        parsed = parse_query(item["pergunta"], retriever.categories, settings.query_focus)
        result = retriever.retrieve(parsed)
        terms = item.get("termos") or []
        hit = None
        if terms and result.evidences:
            texts = [retriever.docs.at[ev.review_id, "texto_norm"] for ev in result.evidences]
            hit = sum(any(term in text for term in terms) for text in texts) / len(texts)
        rows.append(
            {
                "pergunta": item["pergunta"],
                "no_escopo": item["no_escopo"],
                "filtros_inferidos": parsed.filters,
                "filtros_ok": parsed.filters == item.get("filtros", {}),
                "relevancia_termos": hit,
                "sim_max": round(result.max_similarity, 3),
                "sim_suporte": round(result.support_similarity, 3),
            }
        )

    inside = [r["sim_suporte"] for r in rows if r["no_escopo"]]
    outside = [r["sim_suporte"] for r in rows if not r["no_escopo"]]
    threshold, accuracy = _best_threshold(inside, outside)
    hits = [r["relevancia_termos"] for r in rows if r["relevancia_termos"] is not None]
    at_current = sum((r["sim_suporte"] >= current) == r["no_escopo"] for r in rows) / len(rows)

    summary = {
        "backend": retriever.manifest["embedding_model"],
        "perguntas": len(rows),
        "filtros_corretos": f"{sum(r['filtros_ok'] for r in rows)}/{len(rows)}",
        "relevancia_termos_media": round(sum(hits) / len(hits), 3) if hits else None,
        "limiar_atual": current,
        "acuracia_escopo_limiar_atual": round(at_current, 3),
        "limiar_sugerido": threshold,
        "acuracia_escopo_limiar_sugerido": round(accuracy, 3),
        "sim_suporte_no_escopo_min": min(inside) if inside else None,
        "sim_suporte_fora_escopo_max": max(outside) if outside else None,
        "linhas": rows,
    }
    if write:
        manifest = dict(retriever.manifest)
        manifest["min_similarity"] = threshold
        manifest["min_similarity_calibrado"] = True
        write_manifest(settings, manifest)
    return summary


def to_markdown(summary: dict) -> str:
    lines = [
        f"Backend de embeddings: `{summary['backend']}` — {summary['perguntas']} perguntas.",
        "",
        f"- Filtros inferidos corretamente: **{summary['filtros_corretos']}**",
        f"- Relevância@k por termos (média, perguntas no escopo): **{summary['relevancia_termos_media']}**",
        f"- Aceitar/recusar com o limiar atual ({summary['limiar_atual']}): "
        f"**{summary['acuracia_escopo_limiar_atual']:.0%}** de acerto",
        f"- Limiar sugerido: **{summary['limiar_sugerido']}** "
        f"({summary['acuracia_escopo_limiar_sugerido']:.0%} de acerto) — menor suporte no escopo: "
        f"{summary['sim_suporte_no_escopo_min']}, maior suporte fora do escopo: "
        f"{summary['sim_suporte_fora_escopo_max']}",
        "",
        "| Pergunta | No escopo | Filtros ok | Relevância@k | Sim. máx. | Sim. suporte |",
        "|---|---|---|---|---|---|",
    ]
    for r in summary["linhas"]:
        hit = "—" if r["relevancia_termos"] is None else f"{r['relevancia_termos']:.2f}"
        lines.append(
            f"| {r['pergunta']} | {'sim' if r['no_escopo'] else 'não'} | "
            f"{'✓' if r['filtros_ok'] else '✗'} | {hit} | {r['sim_max']} | {r['sim_suporte']} |"
        )
    return "\n".join(lines) + "\n"
