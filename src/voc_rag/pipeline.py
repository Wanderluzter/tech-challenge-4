"""Orquestra o fluxo RAG de ponta a ponta e devolve a resposta com rastro completo."""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

from .config import Settings
from .generator import Generator, build_context
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
    timings_ms: dict = field(default_factory=dict)

    @property
    def cited_evidences(self) -> list[Evidence]:
        return [ev for ev in self.evidences if ev.ref in self.cited_refs]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["retrieval"].pop("evidences", None)
        return data


class RagPipeline:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.retriever = Retriever(self.settings)
        self.generator = Generator(self.settings)

    def ask(self, question: str, manual_filters: Filters | None = None, k: int | None = None) -> RagAnswer:
        timings: dict[str, int] = {}

        # 1) transformação da pergunta
        t0 = time.perf_counter()
        parsed = parse_query(question, self.retriever.categories, self.settings.query_focus)
        filters = merge_filters(parsed.filters, manual_filters)
        timings["pergunta"] = round((time.perf_counter() - t0) * 1000)

        base = dict(question=question, parsed=parsed, filters=filters, timings_ms=timings)

        if len(parsed.search_text) < 3:
            empty = RetrievalResult(
                [], False, "Pergunta vazia.", self.retriever.min_similarity, 0.0, 0.0, 0, 0, 0, 0
            )
            return RagAnswer(
                status="sem_evidencia", answer="Digite uma pergunta sobre as avaliações dos clientes.",
                refusal_stage="recuperacao", refusal_reason="Pergunta vazia.", evidences=[],
                cited_refs=[], retrieval=empty, context=None, **base,
            )

        # 2) recuperação híbrida + seleção + teste de suficiência
        t0 = time.perf_counter()
        retrieval = self.retriever.retrieve(parsed, filters, k)
        timings["recuperacao"] = round((time.perf_counter() - t0) * 1000)

        if not retrieval.sufficient:
            # Sem evidência suficiente, o LLM nem é chamado: nada a alucinar.
            return RagAnswer(
                status="sem_evidencia", answer=REFUSAL, refusal_stage="recuperacao",
                refusal_reason=retrieval.reason, evidences=[], cited_refs=[], retrieval=retrieval,
                context=None, **base,
            )

        # 3) contexto + geração + validação das citações
        context = build_context(clean_text(question), retrieval.evidences, retrieval.stats, filters)
        t0 = time.perf_counter()
        generation = self.generator.generate(context, retrieval.evidences)
        timings["geracao"] = round((time.perf_counter() - t0) * 1000)

        refused = generation.status != "ok"
        return RagAnswer(
            status=generation.status,
            answer=f"{REFUSAL}\n\n{generation.answer}" if refused else generation.answer,
            refusal_stage="geracao" if refused else None,
            refusal_reason=generation.answer if refused else None,
            evidences=retrieval.evidences,
            cited_refs=generation.cited_refs,
            retrieval=retrieval,
            context=context,
            warnings=generation.warnings,
            provider=generation.provider,
            model=generation.model,
            **base,
        )
