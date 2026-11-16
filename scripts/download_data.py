"""Baixa os CSVs do Brazilian E-Commerce Public Dataset by Olist para data/raw/.

Ordem de tentativa:
1. Kaggle (fonte oficial do desafio), via kagglehub — não exige credenciais para datasets
   públicos, mas pode pedir login dependendo da rede;
2. espelho no GitHub da própria Olist (olist/work-at-olist-data), com os mesmos arquivos.

Alternativa manual: baixe o zip em
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data e extraia em data/raw/.
"""
from __future__ import annotations

import shutil
import sys
import urllib.request
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
FILES = [
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "olist_customers_dataset.csv",
]
MIRROR = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/"


def from_kaggle() -> bool:
    try:
        import kagglehub

        source = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
        for name in FILES:
            shutil.copy(source / name, RAW_DIR / name)
        return True
    except Exception as error:  # noqa: BLE001 - qualquer falha cai no espelho
        print(f"Kaggle indisponível ({type(error).__name__}: {error}). Tentando o espelho no GitHub...")
        return False


def from_mirror() -> None:
    for name in FILES:
        print(f"  baixando {name}")
        urllib.request.urlretrieve(MIRROR + name, RAW_DIR / name)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if all((RAW_DIR / name).exists() for name in FILES):
        print(f"Dados já presentes em {RAW_DIR}")
        return 0
    if not from_kaggle():
        from_mirror()
    print(f"OK: {len(FILES)} arquivos em {RAW_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
