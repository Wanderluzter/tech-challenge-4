"""Etapa 1 — construção da base de conhecimento a partir dos CSVs da Olist.

Saída: data/processed/documents.parquet (1 linha = 1 avaliação = 1 documento) e
data/processed/prep_report.json com o funil de seleção, para justificar cada corte.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import Settings
from .text import clean_text, normalize
from .themes import detect_themes

REQUIRED_FILES = {
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
}


def load_raw(raw_dir: Path) -> dict[str, pd.DataFrame]:
    missing = [name for name in REQUIRED_FILES.values() if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Arquivos ausentes em {raw_dir}: {', '.join(missing)}. "
            "Rode `python scripts/download_data.py` ou baixe o dataset do Kaggle."
        )
    return {key: pd.read_csv(raw_dir / name) for key, name in REQUIRED_FILES.items()}


def _sentiment(score: int) -> str:
    if score <= 2:
        return "negativo"
    return "neutro" if score == 3 else "positivo"


def _order_context(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Uma linha por pedido com os metadados usados como filtro e contexto."""
    orders = raw["orders"].copy()
    for col in (
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ):
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    delivered = orders["order_delivered_customer_date"]
    estimated = orders["order_estimated_delivery_date"]
    # dias além do prazo prometido (negativo = chegou antes); comparação por data, não hora
    orders["dias_atraso"] = (delivered.dt.normalize() - estimated.dt.normalize()).dt.days
    orders["entrega_status"] = "no_prazo"
    orders.loc[orders["dias_atraso"] > 0, "entrega_status"] = "atrasada"
    # sem data de entrega registrada: o pedido não chegou (ou não há registro de que chegou)
    orders.loc[delivered.isna(), "entrega_status"] = "nao_entregue"

    # categoria principal do pedido = categoria do primeiro item
    items = raw["items"].sort_values(["order_id", "order_item_id"])
    items = items.merge(
        raw["products"][["product_id", "product_category_name"]], on="product_id", how="left"
    )
    per_order = items.groupby("order_id").agg(
        categoria=("product_category_name", "first"), n_itens=("order_item_id", "count")
    )

    ctx = orders.merge(per_order, on="order_id", how="left").merge(
        raw["customers"][["customer_id", "customer_state"]], on="customer_id", how="left"
    )
    return ctx[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "dias_atraso",
            "entrega_status",
            "categoria",
            "n_itens",
            "customer_state",
        ]
    ]


def build_documents(raw: dict[str, pd.DataFrame], min_chars: int = 10) -> tuple[pd.DataFrame, dict]:
    """Seleciona, limpa e enriquece as avaliações. Retorna (documentos, relatório)."""
    reviews = raw["reviews"].copy()
    report: dict = {"avaliacoes_no_arquivo": int(len(reviews))}

    # 1) Seleção: só avaliações com algum texto (título ou comentário). ~59% não têm
    #    comentário; não há o que recuperar nelas e imputar texto seria inventar evidência.
    reviews["titulo"] = reviews["review_comment_title"].map(clean_text)
    reviews["comentario"] = reviews["review_comment_message"].map(clean_text)
    has_text = (reviews["titulo"] != "") | (reviews["comentario"] != "")
    report["sem_texto_descartadas"] = int((~has_text).sum())
    reviews = reviews[has_text]

    # 2) Duplicatas: o mesmo review_id pode estar ligado a vários pedidos (compra dividida
    #    entre vendedores). Fica uma linha por avaliação, para não inflar a evidência.
    reviews = reviews.sort_values(["review_id", "review_answer_timestamp"])
    before = len(reviews)
    reviews = reviews.drop_duplicates("review_id", keep="first")
    report["review_id_duplicado_descartadas"] = int(before - len(reviews))

    # 3) Documento = título + comentário. As avaliações são curtas (mediana ~50 caracteres),
    #    então não há chunking: cada avaliação é uma unidade de evidência rastreável.
    title_adds = [
        t if t and normalize(t) not in normalize(c) else ""
        for t, c in zip(reviews["titulo"], reviews["comentario"])
    ]
    reviews["texto"] = [
        f"{t}. {c}" if t and c else (t or c) for t, c in zip(title_adds, reviews["comentario"])
    ]
    reviews["texto_norm"] = reviews["texto"].map(normalize)

    # 4) Textos sem conteúdo informativo ("ok", "bom", "recomendo"): não explicam nada e
    #    competiriam com evidências reais no top-k. A nota deles continua nos dados brutos.
    too_short = reviews["texto_norm"].str.len() < min_chars
    report["texto_curto_descartadas"] = int(too_short.sum())
    reviews = reviews[~too_short]

    # 5) Enriquecimento com metadados do pedido
    docs = reviews.merge(_order_context(raw), on="order_id", how="left")
    purchase = docs["order_purchase_timestamp"]
    docs["review_score"] = docs["review_score"].astype(int)
    docs["sentimento"] = docs["review_score"].map(_sentiment)
    docs["data_compra"] = purchase.dt.strftime("%Y-%m-%d").fillna("")
    docs["ano"] = purchase.dt.year.fillna(0).astype(int)
    docs["ano_mes"] = purchase.dt.strftime("%Y-%m").fillna("")
    # Ausentes nos metadados viram categorias explícitas, nunca um valor "chutado":
    docs["categoria"] = docs["categoria"].fillna("desconhecida")
    docs["uf"] = docs["customer_state"].fillna("desconhecida")
    docs["order_status"] = docs["order_status"].fillna("desconhecido")
    docs["entrega_status"] = docs["entrega_status"].fillna("nao_entregue")
    docs["n_itens"] = docs["n_itens"].fillna(0).astype(int)
    docs["dias_atraso"] = docs["dias_atraso"].astype("Int64")  # nulo quando não foi entregue
    docs["temas"] = docs["texto_norm"].map(lambda t: "|".join(detect_themes(t)))

    docs = docs[
        [
            "review_id",
            "order_id",
            "texto",
            "texto_norm",
            "review_score",
            "sentimento",
            "data_compra",
            "ano",
            "ano_mes",
            "categoria",
            "uf",
            "order_status",
            "entrega_status",
            "dias_atraso",
            "n_itens",
            "temas",
        ]
    ].reset_index(drop=True)

    report["documentos_na_base"] = int(len(docs))
    report["por_nota"] = {int(k): int(v) for k, v in docs["review_score"].value_counts().sort_index().items()}
    report["por_entrega_status"] = {k: int(v) for k, v in docs["entrega_status"].value_counts().items()}
    report["textos_repetidos"] = int(docs["texto_norm"].duplicated().sum())
    report["tamanho_mediano_caracteres"] = int(docs["texto"].str.len().median())
    return docs, report


def run(settings: Settings) -> dict:
    raw = load_raw(settings.raw_dir)
    docs, report = build_documents(raw, settings.min_chars)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    docs.to_parquet(settings.documents_path, index=False)
    (settings.processed_dir / "prep_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report
