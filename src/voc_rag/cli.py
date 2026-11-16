"""Linha de comando: python -m voc_rag.cli {prepare,index,ask,eval,examples}"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT, Settings

EXAMPLE_QUESTIONS = [
    "Quais são os principais problemas relatados pelos clientes?",
    "Quais reclamações relacionadas à entrega aparecem com maior frequência?",
    "O que os clientes mais elogiam em suas experiências de compra?",
    "Quais problemas são relatados por clientes insatisfeitos?",
    "Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?",
    "O que os clientes mais elogiam na categoria beleza e saúde?",
    "Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?",
    "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
    "Qual é a capital da França?",
    "O que os clientes acham do tempo de bateria do iPhone 15?",
]


def render_answer(result, show_all: bool = True) -> str:
    """Resposta + evidências em Markdown (usado no terminal e em docs/EXEMPLOS.md)."""
    lines = [f"**Pergunta:** {result.question}", ""]
    lines.append("**Transformação da pergunta:** " + "; ".join(result.parsed.notes))
    lines.append(f"**Filtros aplicados:** `{json.dumps(result.filters, ensure_ascii=False)}`")
    r = result.retrieval
    if len(r.queries) > 1:
        lines.append("**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** " + " | ".join(f"“{q}”" for q in r.queries))
    lines.append(
        f"**Recuperação:** {r.n_dense} candidatos densos + {r.n_bm25} lexicais → "
        f"{r.n_candidates} únicos → {r.n_above_threshold} acima do limiar {r.min_similarity:.2f} → "
        f"{len(result.evidences)} no contexto (similaridade máx. {r.max_similarity:.2f})"
    )
    lines += ["", f"**Status:** {result.status}" + (f" (recusa na etapa de {result.refusal_stage})" if result.refusal_stage else ""), ""]
    lines += [result.answer, ""]
    if result.refusal_reason and result.refusal_stage == "recuperacao":
        lines += [f"_Motivo: {result.refusal_reason}_", ""]
    for warning in result.warnings:
        lines.append(f"> Aviso: {warning}")
    evidences = result.evidences if show_all else result.cited_evidences
    if evidences:
        lines += ["**Evidências (avaliações recuperadas):**", ""]
        for ev in evidences:
            mark = "citada" if ev.ref in result.cited_refs else "não citada"
            lines.append(
                f"- **[{ev.ref}]** `{ev.review_id}` · nota {ev.review_score} · {ev.data_compra} · "
                f"{ev.categoria} · entrega {ev.entrega_status} · sim {ev.similarity:.2f} · {mark}  \n"
                f"  “{ev.texto}”"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="voc_rag", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare", help="CSV brutos → base de documentos (parquet)")
    sub.add_parser("index", help="gera embeddings e indexa no ChromaDB")
    ask = sub.add_parser("ask", help="faz uma pergunta ao pipeline RAG")
    ask.add_argument("question")
    ask.add_argument("--json", action="store_true", help="saída completa em JSON")
    ev = sub.add_parser("eval", help="avalia a recuperação e calibra o limiar de similaridade")
    ev.add_argument("--questions", default=str(ROOT / "eval" / "perguntas.json"))
    ev.add_argument("--write", action="store_true", help="grava o limiar sugerido no manifesto do índice")
    ev.add_argument("--out", default=str(ROOT / "eval" / "resultado.md"))
    ev.add_argument("--e2e", action="store_true", help="roda também o pipeline completo (usa o LLM)")
    ex = sub.add_parser("examples", help="gera docs/EXEMPLOS.md com perguntas e respostas reais")
    ex.add_argument("--out", default=str(ROOT / "docs" / "EXEMPLOS.md"))
    args = parser.parse_args(argv)
    settings = Settings()

    if args.command == "prepare":
        from . import data_prep

        print(json.dumps(data_prep.run(settings), ensure_ascii=False, indent=2))
    elif args.command == "index":
        from . import index

        print(json.dumps(index.build(settings), ensure_ascii=False, indent=2))
    elif args.command == "ask":
        from .pipeline import RagPipeline

        result = RagPipeline(settings).ask(args.question)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
        else:
            print(render_answer(result))
    elif args.command == "eval":
        from . import evaluation

        summary = evaluation.run(settings, Path(args.questions), write=args.write)
        report = evaluation.to_markdown(summary)
        if args.write:
            settings = Settings()
        structured = {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "recuperacao": summary, "ponta_a_ponta": None}
        if args.e2e:
            structured["ponta_a_ponta"] = evaluation.run_e2e(settings, Path(args.questions))
            report += "\n" + evaluation.e2e_to_markdown(structured["ponta_a_ponta"])
        Path(args.out).write_text(report, encoding="utf-8")
        # versão estruturada, lida pelo dashboard de qualidade
        Path(args.out).with_suffix(".json").write_text(
            json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(report)
        if args.write:
            print(f"Limiar {summary['limiar_sugerido']} gravado em {settings.manifest_path}")
    elif args.command == "examples":
        from .pipeline import RagPipeline

        pipeline = RagPipeline(settings)
        manifest = pipeline.retriever.manifest
        parts = [
            "# Exemplos de perguntas e respostas",
            "",
            "Gerado por `python -m voc_rag.cli examples` sobre a base real da Olist. "
            "Nada aqui foi editado à mão.",
            "",
            f"- Embeddings: `{manifest['embedding_model']}`",
            f"- Geração: `{pipeline.generator.provider}`"
            + (f" / `{settings.llm_model}`" if pipeline.generator.provider != "extractive" else " (sem LLM)"),
            f"- Limiar de similaridade: {pipeline.retriever.min_similarity}",
            "",
        ]
        from .evaluation import FALLBACK, ask_with_retry

        for i, question in enumerate(EXAMPLE_QUESTIONS, start=1):
            print(f"[{i}/{len(EXAMPLE_QUESTIONS)}] {question}", file=sys.stderr)
            result = ask_with_retry(pipeline, question)
            if result.provider == FALLBACK:
                print("LLM indisponível; EXEMPLOS.md não foi reescrito.", file=sys.stderr)
                return 1
            parts += [f"## {i}. {question}", "", render_answer(result), "---", ""]
        Path(args.out).write_text("\n".join(parts), encoding="utf-8")
        print(f"Escrito em {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
