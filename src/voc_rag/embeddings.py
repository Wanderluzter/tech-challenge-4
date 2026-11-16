"""Representação vetorial de documentos e perguntas.

Dois backends com a mesma interface (vetores L2-normalizados, cosseno = produto interno):

- "e5"  (padrão): intfloat/multilingual-e5-small via sentence-transformers. Modelo
  multilíngue treinado para busca assimétrica (pergunta curta x passagem), 384 dimensões,
  roda em CPU. Exige os prefixos "query: " e "passage: ".
- "lsa" (fallback offline): TF-IDF de n-gramas de caracteres + SVD truncado, ajustado na
  própria base. Não baixa nada; serve para testes, CI e ambientes sem acesso ao
  Hugging Face. Captura bem variação de grafia, mas não sinonímia como o e5.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from .text import normalize


class Embedder(Protocol):
    name: str

    def embed_documents(self, texts: list[str]) -> np.ndarray: ...

    def embed_query(self, text: str) -> np.ndarray: ...


def _l2(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return (matrix / np.clip(norms, 1e-12, None)).astype(np.float32)


class E5Embedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # import tardio: é pesado

        self.name = model_name
        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(
            [f"passage: {t}" for t in texts],
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 500,
            convert_to_numpy=True,
        ).astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        return self._model.encode(
            [f"query: {text}"], normalize_embeddings=True, convert_to_numpy=True
        )[0].astype(np.float32)


class LsaEmbedder:
    FILE = "lsa_model.joblib"

    def __init__(self, dim: int = 256):
        self.name = f"lsa-tfidf-char-svd{dim}"
        self.dim = dim
        self._pipeline = None

    def fit(self, texts: list[str]) -> "LsaEmbedder":
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import make_pipeline

        vectorizer = TfidfVectorizer(
            preprocessor=normalize, analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True
        )
        n_features = len(vectorizer.fit(texts).vocabulary_)
        svd = TruncatedSVD(n_components=max(2, min(self.dim, n_features - 1)), random_state=42)
        self._pipeline = make_pipeline(vectorizer, svd).fit(texts)
        return self

    def save(self, index_dir: Path) -> None:
        import joblib

        joblib.dump(self._pipeline, index_dir / self.FILE)

    @classmethod
    def load(cls, index_dir: Path) -> "LsaEmbedder":
        import joblib

        instance = cls()
        instance._pipeline = joblib.load(index_dir / cls.FILE)
        return instance

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return _l2(self._pipeline.transform(texts))

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_documents([text])[0]


def load_embedder(backend: str, model_name: str, index_dir: Path) -> Embedder:
    """Carrega o embedder para consulta — o mesmo backend usado para construir o índice."""
    if backend == "e5":
        return E5Embedder(model_name)
    if backend == "lsa":
        return LsaEmbedder.load(index_dir)
    raise ValueError(f"EMBEDDING_BACKEND desconhecido: {backend!r} (use 'e5' ou 'lsa')")
