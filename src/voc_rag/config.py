"""Configuração central. Tudo pode ser sobrescrito por variáveis de ambiente (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:  # o .env é opcional; vale o da raiz do repositório
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:  # pragma: no cover
    pass

# Limiar inicial de similaridade (cosseno) por backend de embeddings.
# São pontos de partida: rode `python -m voc_rag.cli eval --write` para calibrar
# com as perguntas de eval/perguntas.json e gravar o valor no manifesto do índice.
DEFAULT_MIN_SIMILARITY = {"e5": 0.80, "lsa": 0.30}


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


@dataclass
class Settings:
    raw_dir: Path = field(default_factory=lambda: Path(_env("RAW_DIR", str(ROOT / "data" / "raw"))))
    processed_dir: Path = field(
        default_factory=lambda: Path(_env("PROCESSED_DIR", str(ROOT / "data" / "processed")))
    )
    index_dir: Path = field(default_factory=lambda: Path(_env("INDEX_DIR", str(ROOT / "data" / "index"))))

    # --- preparação da base
    min_chars: int = field(default_factory=lambda: int(_env("MIN_CHARS", "10")))

    # --- embeddings
    embedding_backend: str = field(default_factory=lambda: _env("EMBEDDING_BACKEND", "e5"))
    embedding_model: str = field(
        default_factory=lambda: _env("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    )

    # --- recuperação
    # remove o vocabulário analítico da pergunta antes da busca (ver query.py)
    query_focus: bool = field(default_factory=lambda: _env("QUERY_FOCUS", "on").lower() != "off")
    dense_candidates: int = field(default_factory=lambda: int(_env("DENSE_CANDIDATES", "40")))
    bm25_candidates: int = field(default_factory=lambda: int(_env("BM25_CANDIDATES", "40")))
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "12")))
    mmr_lambda: float = field(default_factory=lambda: float(_env("MMR_LAMBDA", "0.7")))
    min_evidences: int = field(default_factory=lambda: int(_env("MIN_EVIDENCES", "3")))
    # vazio = usa o valor calibrado no manifesto do índice ou o padrão do backend
    min_similarity: float | None = field(
        default_factory=lambda: float(os.environ["MIN_SIMILARITY"])
        if os.getenv("MIN_SIMILARITY")
        else None
    )

    # --- geração
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "auto"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", ""))
    llm_base_url: str | None = field(default_factory=lambda: os.getenv("LLM_BASE_URL") or None)
    llm_api_key: str | None = field(
        default_factory=lambda: os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or None
    )
    llm_temperature: float = field(default_factory=lambda: float(_env("LLM_TEMPERATURE", "0.1")))

    @property
    def documents_path(self) -> Path:
        return self.processed_dir / "documents.parquet"

    @property
    def manifest_path(self) -> Path:
        return self.index_dir / "manifest.json"

    def resolved_llm_provider(self) -> str:
        """'auto' vira 'openai_compat' se houver chave/endpoint; senão, modo extrativo."""
        if self.llm_provider != "auto":
            return self.llm_provider
        return "openai_compat" if (self.llm_api_key or self.llm_base_url) else "extractive"
