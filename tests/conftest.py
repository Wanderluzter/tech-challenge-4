"""Base sintética mínima, no formato dos CSVs da Olist, para testar o pipeline sem downloads.

Os textos são inventados para o teste; nenhum dado real da Olist é usado aqui.
"""
from __future__ import annotations

import itertools

import pandas as pd
import pytest

from voc_rag import data_prep, index
from voc_rag.config import Settings

TEMPLATES = {
    1: [
        "Não recebi o produto {x}, o prazo de entrega já venceu e ninguém responde",
        "Produto {x} veio quebrado e com defeito, quero meu dinheiro de volta",
        "Entrega muito atrasada, o pedido {x} demorou mais de um mês para chegar",
        "Veio produto errado, pedi {x} e recebi outro produto diferente do anúncio",
    ],
    5: [
        "Produto {x} excelente, ótima qualidade e chegou antes do prazo",
        "Entrega rápida, {x} muito bem embalado, recomendo a loja",
        "Adorei o {x}, produto de qualidade e entrega dentro do prazo",
    ],
    3: ["O {x} é razoável, a qualidade do material poderia ser melhor pelo preço"],
}
ITEMS = ["relógio", "perfume", "teclado", "tapete", "fone", "brinquedo", "cadeira", "mochila"]
CATEGORIES = ["relogios_presentes", "beleza_saude", "informatica_acessorios", "cama_mesa_banho"]


def _raw_frames() -> dict[str, pd.DataFrame]:
    reviews, orders, items, products, customers = [], [], [], [], []
    combos = itertools.cycle(CATEGORIES)
    n = 0
    for score, templates in TEMPLATES.items():
        for template in templates:
            for item in ITEMS:
                n += 1
                late = score == 1 and "atrasada" in template
                missing = score == 1 and "Não recebi" in template
                orders.append(
                    {
                        "order_id": f"o{n}",
                        "customer_id": f"c{n}",
                        "order_status": "shipped" if missing else "delivered",
                        "order_purchase_timestamp": f"201{7 + n % 2}-03-{1 + n % 27:02d} 10:00:00",
                        "order_approved_at": None,
                        "order_delivered_carrier_date": None,
                        "order_delivered_customer_date": None
                        if missing
                        else ("2018-06-20 12:00:00" if late else "2018-04-10 12:00:00"),
                        "order_estimated_delivery_date": "2018-05-01 00:00:00",
                    }
                )
                reviews.append(
                    {
                        "review_id": f"r{n}",
                        "order_id": f"o{n}",
                        "review_score": score,
                        "review_comment_title": "Recomendo" if score == 5 and n % 2 else None,
                        "review_comment_message": template.format(x=item),
                        "review_creation_date": "2018-05-02 00:00:00",
                        "review_answer_timestamp": "2018-05-03 00:00:00",
                    }
                )
                items.append({"order_id": f"o{n}", "order_item_id": 1, "product_id": f"p{n}"})
                products.append({"product_id": f"p{n}", "product_category_name": next(combos)})
                customers.append({"customer_id": f"c{n}", "customer_state": "SP" if n % 2 else "RJ"})

    # casos de borda da preparação
    reviews += [
        {"review_id": "vazio", "order_id": "o1", "review_score": 5, "review_comment_title": None,
         "review_comment_message": None, "review_creation_date": "", "review_answer_timestamp": ""},
        {"review_id": "curto", "order_id": "o2", "review_score": 5, "review_comment_title": None,
         "review_comment_message": "ok", "review_creation_date": "", "review_answer_timestamp": ""},
        {"review_id": "r1", "order_id": "o3", "review_score": 1, "review_comment_title": None,
         "review_comment_message": "duplicata do review r1 em outro pedido", "review_creation_date": "",
         "review_answer_timestamp": "2019-01-01 00:00:00"},
        {"review_id": "orfao", "order_id": "nao-existe", "review_score": 2, "review_comment_title": None,
         "review_comment_message": "Comentário   com\r\nquebra de linha e pedido inexistente",
         "review_creation_date": "", "review_answer_timestamp": ""},
    ]
    return {
        "reviews": pd.DataFrame(reviews),
        "orders": pd.DataFrame(orders),
        "items": pd.DataFrame(items),
        "products": pd.DataFrame(products),
        "customers": pd.DataFrame(customers),
    }


@pytest.fixture(scope="session")
def raw() -> dict[str, pd.DataFrame]:
    return _raw_frames()


@pytest.fixture(scope="session")
def settings(tmp_path_factory, raw) -> Settings:
    """Base preparada e indexada com o backend offline (LSA), sem LLM."""
    root = tmp_path_factory.mktemp("voc")
    raw_dir = root / "raw"
    raw_dir.mkdir()
    for key, name in data_prep.REQUIRED_FILES.items():
        raw[key].to_csv(raw_dir / name, index=False)
    cfg = Settings(
        raw_dir=raw_dir,
        processed_dir=root / "processed",
        index_dir=root / "index",
        embedding_backend="lsa",
        llm_provider="extractive",
        min_similarity=0.5,
        top_k=6,
    )
    data_prep.run(cfg)
    index.build(cfg)
    return cfg
