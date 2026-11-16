"""Etapa 2 — embeddings e indexação no banco vetorial (ChromaDB persistente, cosseno/HNSW)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import DEFAULT_MIN_SIMILARITY, Settings
from .embeddings import E5Embedder, LsaEmbedder

COLLECTION = "avaliacoes_olist"
# Metadados gravados no Chroma: são os campos usados como filtro na recuperação.
METADATA_FIELDS = ["review_score", "ano", "categoria", "uf", "entrega_status", "sentimento"]


def open_collection(index_dir: Path, create: bool = False):
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    client = chromadb.PersistentClient(
        path=str(index_dir / "chroma"), settings=ChromaSettings(anonymized_telemetry=False)
    )
    if create:
        return client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    return client.get_collection(COLLECTION)


def read_manifest(settings: Settings) -> dict:
    if not settings.manifest_path.exists():
        raise FileNotFoundError(
            f"Índice não encontrado em {settings.index_dir}. Rode `python -m voc_rag.cli index`."
        )
    return json.loads(settings.manifest_path.read_text(encoding="utf-8"))


def write_manifest(settings: Settings, manifest: dict) -> None:
    settings.manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def build(settings: Settings, batch_size: int = 2000) -> dict:
    if not settings.documents_path.exists():
        raise FileNotFoundError(
            f"{settings.documents_path} não existe. Rode `python -m voc_rag.cli prepare` antes."
        )
    docs = pd.read_parquet(settings.documents_path)
    texts = docs["texto"].tolist()

    if settings.index_dir.exists():  # reconstrução completa: evita índice misturado
        shutil.rmtree(settings.index_dir)
    settings.index_dir.mkdir(parents=True)

    if settings.embedding_backend == "e5":
        embedder = E5Embedder(settings.embedding_model)
    elif settings.embedding_backend == "lsa":
        embedder = LsaEmbedder().fit(texts)
        embedder.save(settings.index_dir)
    else:
        raise ValueError(f"EMBEDDING_BACKEND desconhecido: {settings.embedding_backend!r}")

    collection = open_collection(settings.index_dir, create=True)
    dim = 0
    for start in range(0, len(docs), batch_size):
        chunk = docs.iloc[start : start + batch_size]
        vectors = embedder.embed_documents(chunk["texto"].tolist())
        dim = int(vectors.shape[1])
        collection.add(
            ids=chunk["review_id"].tolist(),
            embeddings=vectors,
            documents=chunk["texto"].tolist(),
            metadatas=[
                {key: (value.item() if hasattr(value, "item") else value) for key, value in row.items()}
                for row in chunk[METADATA_FIELDS].to_dict("records")
            ],
        )
        print(f"  indexados {min(start + batch_size, len(docs))}/{len(docs)}", flush=True)

    manifest = {
        "embedding_backend": settings.embedding_backend,
        "embedding_model": embedder.name,
        "dimensoes": dim,
        "documentos": int(len(docs)),
        "min_similarity": DEFAULT_MIN_SIMILARITY[settings.embedding_backend],
        "min_similarity_calibrado": False,
        "criado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_manifest(settings, manifest)
    return manifest
