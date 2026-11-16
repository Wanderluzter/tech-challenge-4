"""Limpeza e normalização de texto, compartilhadas entre a base e as perguntas."""
from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_CTRL = re.compile(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]")
_REPEAT = re.compile(r"(.)\1{3,}")  # "ótimoooooo" -> "ótimoo"
_NON_WORD = re.compile(r"[^a-z0-9 ]+")

# Stopwords mínimas para o BM25. "nao", "sem" e "nunca" ficam de fora de propósito:
# a negação muda o sentido de uma avaliação ("recebi" x "não recebi").
STOPWORDS = frozenset(
    """a o as os um uma uns umas de do da dos das em no na nos nas por para pra com e ou que
    se eu me meu minha ele ela eles elas isso esse essa este esta foi ser era e ao aos mas
    como mais muito ja tambem so quando qual quais sobre the pelo pela pelos pelas seu sua
    ate entre lhe nem ha tem ter esta estao sao""".split()
)


def clean_text(value: object) -> str:
    """Limpeza leve do texto original (preserva acentos e caixa para o LLM e o embedding)."""
    if value is None or (isinstance(value, float) and value != value):  # NaN
        return ""
    text = unicodedata.normalize("NFC", str(value))
    text = _CTRL.sub(" ", text)
    text = _WS.sub(" ", text)  # quebras de linha e espaços repetidos
    text = _REPEAT.sub(r"\1\1", text)
    return text.strip()


def normalize(text: str) -> str:
    """Forma canônica para busca lexical e regras: minúsculas, sem acento, sem pontuação."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _NON_WORD.sub(" ", text)
    return _WS.sub(" ", text).strip()


def tokenize(text: str) -> list[str]:
    """Tokens para o BM25 (já normalizados e sem stopwords)."""
    return [tok for tok in normalize(text).split() if tok not in STOPWORDS and len(tok) > 1]
