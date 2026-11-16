"""API HTTP do RAG, consumida pela interface React (web/).

    uvicorn voc_rag.api:app --port 8000

Com `web/dist` construído (`npm run build` em web/), a mesma porta também serve a interface.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import ROOT, Settings
from .dashboard import DELIVERY_LABELS, base_metrics, log_query, quality_metrics, usage_metrics

WEB_DIST = ROOT / "web" / "dist"
EXAMPLES = [
    "Quais são os principais problemas relatados pelos clientes?",
    "Quais reclamações relacionadas à entrega aparecem com maior frequência?",
    "O que os clientes mais elogiam em suas experiências de compra?",
    "O que os clientes mais elogiam na categoria beleza e saúde?",
    "O que os clientes dizem sobre a embalagem dos produtos?",
    "Qual é a capital da França?",
]


class ScoreRange(BaseModel):
    gte: int = Field(1, ge=1, le=5)
    lte: int = Field(5, ge=1, le=5)


class ManualFilters(BaseModel):
    review_score: ScoreRange | None = None
    ano: int | None = None
    categoria: str | None = None
    entrega_status: list[str] | None = None
    uf: str | None = None

    def to_filters(self) -> dict:
        filters = self.model_dump(exclude_none=True)
        score = filters.get("review_score")
        if score and score == {"gte": 1, "lte": 5}:
            filters.pop("review_score")
        return {k: v for k, v in filters.items() if v not in ("", [])}


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    filters: ManualFilters | None = None
    top_k: int | None = Field(None, ge=4, le=20)
    model: str | None = Field(None, max_length=200)


def _logs_path(settings: Settings) -> Path:
    return settings.processed_dir.parent / "logs" / "perguntas.jsonl"


@lru_cache(maxsize=1)
def get_pipeline():
    from .pipeline import RagPipeline

    return RagPipeline()


@lru_cache(maxsize=1)
def get_base_metrics() -> dict:
    return base_metrics(get_pipeline().retriever.docs)


def _pipeline_or_503():
    try:
        return get_pipeline()
    except FileNotFoundError as error:
        raise HTTPException(503, f"{error} Siga o passo a passo do README.") from error


app = FastAPI(title="Voz do Cliente — Olist", version="1.0")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict:
    pipeline = _pipeline_or_503()
    retriever, settings = pipeline.retriever, pipeline.settings
    provider = pipeline.generator.provider
    return {
        "documentos": retriever.manifest["documentos"],
        "embeddings": retriever.manifest["embedding_model"],
        "provedor": provider,
        "modelo": settings.llm_model if provider != "extractive" else None,
        "modelos": pipeline.generator.model_status(),
        "limiar": retriever.min_similarity,
        "top_k": settings.top_k,
        "categorias": retriever.categories,
        "ufs": sorted(retriever.docs["uf"].dropna().unique().tolist()),
        "anos": sorted(int(a) for a in retriever.docs["ano"].dropna().unique()),
        "entrega": [{"valor": k, "rotulo": v} for k, v in DELIVERY_LABELS.items()],
        "exemplos": EXAMPLES,
    }


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    pipeline = _pipeline_or_503()
    manual = request.filters.to_filters() if request.filters else None
    if manual and manual.get("categoria") and manual["categoria"] not in pipeline.retriever.categories:
        raise HTTPException(422, f"Categoria desconhecida: {manual['categoria']}")
    if request.model and request.model not in pipeline.generator.models:
        raise HTTPException(422, f"Modelo não configurado: {request.model}")
    result = pipeline.ask(request.question.strip(), manual or None, request.top_k, request.model)
    try:
        log_query(_logs_path(pipeline.settings), result, manual)
    except OSError:
        pass  # falha ao registrar uso não pode impedir a resposta
    data = result.to_dict()
    data["cited_refs"] = sorted(result.cited_refs)
    return data


@app.get("/api/models")
def models() -> list[dict]:
    """Modelos configurados (LLM_MODEL + LLM_FALLBACK_MODELS) e o estado de cada um."""
    return _pipeline_or_503().generator.model_status()


@app.get("/api/dashboard/base")
def dashboard_base() -> dict:
    _pipeline_or_503()
    return get_base_metrics()


@app.get("/api/dashboard/uso")
def dashboard_usage() -> dict:
    return usage_metrics(_logs_path(Settings()))


@app.get("/api/dashboard/qualidade")
def dashboard_quality() -> dict:
    data = quality_metrics(ROOT / "eval" / "resultado.json")
    if data is None:
        raise HTTPException(404, "Rode `python -m voc_rag.cli eval --write --e2e` para gerar eval/resultado.json.")
    return data


# ----------------------------------------------------------------- interface React (build)
if WEB_DIST.exists():
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        target = WEB_DIST / path
        if path and target.is_file() and WEB_DIST in target.resolve().parents:
            return FileResponse(target)
        return FileResponse(WEB_DIST / "index.html")
