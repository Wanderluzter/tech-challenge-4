"""Orquestra o fluxo RAG de ponta a ponta e devolve a resposta com rastro completo.

O fluxo é um grafo do LangGraph (`StateGraph`): cada etapa é um nó que lê e escreve um
estado tipado, e as duas recusas antes do LLM são arestas condicionais.

    interpretar ──(pergunta vazia)──▶ FIM
         │
    recuperar ──(evidência insuficiente)──▶ FIM      ← o LLM nem é chamado
         │
       gerar (chain LCEL + validação das citações) ──▶ FIM
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .config import Settings
from .generator import Generation, Generator, build_context
from .text import clean_text
from .query import Filters, ParsedQuery, merge_filters, parse_query
from .retriever import Evidence, RetrievalResult, Retriever

REFUSAL = (
    "Não encontrei evidências suficientes nas avaliações dos clientes para responder a essa "
    "pergunta com segurança."
)


@dataclass
class RagAnswer:
    question: str
    status: str  # "ok" | "sem_evidencia"
    answer: str
    refusal_stage: str | None  # "recuperacao" | "geracao" | None
    refusal_reason: str | None
    parsed: ParsedQuery
    filters: Filters
    evidences: list[Evidence]
    cited_refs: list[int]
    retrieval: RetrievalResult
    context: str | None
    warnings: list[str] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    requested_model: str = ""
    timings_ms: dict = field(default_factory=dict)

    @property
    def cited_evidences(self) -> list[Evidence]:
        return [ev for ev in self.evidences if ev.ref in self.cited_refs]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["retrieval"].pop("evidences", None)
        return data


class RagState(TypedDict, total=False):
    """Estado compartilhado pelos nós do grafo."""

    question: str
    manual_filters: Filters | None
    k: int | None
    model: str | None
    allow_fallback: bool
    parsed: ParsedQuery
    filters: Filters
    retrieval: RetrievalResult
    context: str | None
    generation: Generation | None
    timings_ms: dict


def _elapsed_ms(t0: float) -> int:
    return round((time.perf_counter() - t0) * 1000)


class RagPipeline:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.retriever = Retriever(self.settings)
        self.generator = Generator(self.settings)
        self.graph = self._build_graph()

    # ------------------------------------------------------------ grafo
    def _build_graph(self):
        graph = StateGraph(RagState)
        graph.add_node("interpretar", self._interpret)
        graph.add_node("recuperar", self._retrieve)
        graph.add_node("gerar", self._generate)
        graph.add_edge(START, "interpretar")
        graph.add_conditional_edges(
            "interpretar", lambda s: "recuperar" if len(s["parsed"].search_text) >= 3 else END,
            ["recuperar", END],
        )
        # Sem evidência suficiente, o LLM nem é chamado: nada a alucinar.
        graph.add_conditional_edges(
            "recuperar", lambda s: "gerar" if s["retrieval"].sufficient else END, ["gerar", END]
        )
        graph.add_edge("gerar", END)
        return graph.compile()

    def _interpret(self, state: RagState) -> dict:
        """1) transformação da pergunta: foco, filtros inferidos e filtros manuais."""
        t0 = time.perf_counter()
        parsed = parse_query(state["question"], self.retriever.categories, self.settings.query_focus)
        filters = merge_filters(parsed.filters, state.get("manual_filters"))
        return {"parsed": parsed, "filters": filters, "timings_ms": {"pergunta": _elapsed_ms(t0)}}

    def _retrieve(self, state: RagState) -> dict:
        """2) recuperação híbrida + seleção + teste de suficiência."""
        t0 = time.perf_counter()
        retrieval = self.retriever.retrieve(state["parsed"], state["filters"], state.get("k"))
        return {"retrieval": retrieval, "timings_ms": {**state["timings_ms"], "recuperacao": _elapsed_ms(t0)}}

    def _generate(self, state: RagState) -> dict:
        """3) contexto + geração (chain LCEL) + validação das citações."""
        retrieval = state["retrieval"]
        context = build_context(clean_text(state["question"]), retrieval.evidences, retrieval.stats, state["filters"])
        t0 = time.perf_counter()
        generation = self.generator.generate(
            context, retrieval.evidences, state.get("model"), state.get("allow_fallback", True)
        )
        return {
            "context": context,
            "generation": generation,
            "timings_ms": {**state["timings_ms"], "geracao": _elapsed_ms(t0)},
        }

    # ------------------------------------------------------------ entrada pública
    def ask(
        self,
        question: str,
        manual_filters: Filters | None = None,
        k: int | None = None,
        model: str | None = None,
        allow_fallback: bool = True,
    ) -> RagAnswer:
        state: RagState = self.graph.invoke(
            {"question": question, "manual_filters": manual_filters, "k": k, "model": model,
             "allow_fallback": allow_fallback},
            config={"run_name": "voc_rag", "metadata": {"pergunta": question}},
        )
        return self._to_answer(state, model)

    def _to_answer(self, state: RagState, model: str | None) -> RagAnswer:
        base = dict(
            question=state["question"], parsed=state["parsed"], filters=state["filters"],
            timings_ms=state["timings_ms"],
        )
        retrieval = state.get("retrieval")
        if retrieval is None:  # parou em "interpretar"
            empty = RetrievalResult(
                [], False, "Pergunta vazia.", self.retriever.min_similarity, 0.0, 0.0, 0, 0, 0, 0
            )
            return RagAnswer(
                status="sem_evidencia", answer="Digite uma pergunta sobre as avaliações dos clientes.",
                refusal_stage="recuperacao", refusal_reason="Pergunta vazia.", evidences=[],
                cited_refs=[], retrieval=empty, context=None, **base,
            )

        generation = state.get("generation")
        if generation is None:  # parou em "recuperar"
            return RagAnswer(
                status="sem_evidencia", answer=REFUSAL, refusal_stage="recuperacao",
                refusal_reason=retrieval.reason, evidences=[], cited_refs=[], retrieval=retrieval,
                context=None, **base,
            )

        refused = generation.status != "ok"
        return RagAnswer(
            status=generation.status,
            answer=f"{REFUSAL}\n\n{generation.answer}" if refused else generation.answer,
            refusal_stage="geracao" if refused else None,
            refusal_reason=generation.answer if refused else None,
            evidences=retrieval.evidences,
            cited_refs=generation.cited_refs,
            retrieval=retrieval,
            context=state["context"],
            warnings=generation.warnings,
            provider=generation.provider,
            model=generation.model,
            requested_model=(model if model in self.generator.models else (self.generator.models or [""])[0]),
            **base,
        )
