"""Taxonomia de temas por regras (regex) aplicada na ingestão.

Por que existe: a recuperação top-k traz *exemplos* relevantes, mas não sabe contar.
Perguntas como "quais reclamações aparecem com maior frequência?" pedem uma noção de
volume. Marcamos cada avaliação com temas simples e transparentes na ingestão e, na
consulta, entregamos ao modelo um panorama quantitativo do recorte (ver retriever.py).

As regras rodam sobre o texto normalizado (minúsculas, sem acento). São uma aproximação
auditável, não um classificador: a contagem é sempre apresentada como "aproximada".
"""
from __future__ import annotations

import re

_NEG_PRAZO = re.compile(r"nao (chegou|entreg\w*|foi entregue|veio|recebi) (no|dentro do) prazo")

THEME_PATTERNS: dict[str, re.Pattern[str]] = {
    "entrega_atrasada": re.compile(
        r"atras|demor|fora do prazo|depois do prazo|prazo (vencid|estour|expir)|passou do prazo"
    ),
    "produto_nao_recebido": re.compile(
        r"nao recebi|nao chegou|nao foi entregue|nunca chegou|nao entreg|nao me entreg"
        r"|aguardando (o |a )?(produto|entrega|pedido)|ainda nao (recebi|chegou)"
    ),
    "entrega_incompleta": re.compile(
        r"faltando|faltou|incomplet|parte do pedido|(so|apenas|somente) (recebi|veio|chegou|entregaram)"
        r"|veio (so|apenas|somente)|recebi (so|apenas|somente)|falta (um|uma|o|a|entregar)"
    ),
    "entrega_no_prazo": re.compile(
        r"antes do prazo|dentro do prazo|no prazo|entrega (super |muito |bem )?rapida"
        r"|chegou (super |muito |bem )?rapido|entrega (foi )?(super |muito )?rapid"
    ),
    "produto_com_defeito": re.compile(
        r"defeit|quebrad|danificad|estragad|nao funciona|parou de funcionar|rasgad|amassad"
        r"|trincad|avaria|arranhad"
    ),
    "produto_errado": re.compile(
        r"produto errado|veio errad|vier(am)? errad|diferente d[oae]|nao (e|era|foi) o que"
        r"|outro produto|(cor|modelo|tamanho) errad|produto trocad|veio trocad|veio outr"
    ),
    "qualidade_baixa": re.compile(
        r"(ma|pessima|baixa|pouca) qualidade|qualidade (ruim|inferior|pessima|baixa|deixa)"
        r"|material (ruim|fraco|fragil|inferior)|falsificad|nao e original|fraquinh|muito fragil"
    ),
    "qualidade_boa": re.compile(
        r"(otima|boa|excelente|alta) qualidade|qualidade (otima|boa|excelente)|bem acabad"
        r"|(otimo|excelente|bom|lindo|maravilhoso) produto|produto (otimo|excelente|muito bom|bom|lindo|de qualidade)"
    ),
    "atendimento": re.compile(
        r"atendimento|sem resposta|nao respond|sem retorno|nao (me )?retorn|entrei em contato"
        r"|tentei contato|\bsac\b|descaso|ninguem (me )?(respond|resolv|atend)"
    ),
    "devolucao_reembolso": re.compile(
        r"devol|reembols|estorn|\btroca\b|trocar|dinheiro de volta|cancel"
    ),
    "recomendacao": re.compile(r"recomend|indico|super indico"),
}

THEME_LABELS = {
    "entrega_atrasada": "Entrega atrasada / demora",
    "produto_nao_recebido": "Produto não recebido",
    "entrega_incompleta": "Entrega incompleta / itens faltando",
    "entrega_no_prazo": "Entrega rápida ou no prazo",
    "produto_com_defeito": "Produto com defeito ou danificado",
    "produto_errado": "Produto errado ou diferente do anunciado",
    "qualidade_baixa": "Qualidade abaixo do esperado",
    "qualidade_boa": "Boa qualidade do produto",
    "atendimento": "Atendimento / falta de retorno",
    "devolucao_reembolso": "Devolução, troca, cancelamento ou reembolso",
    "recomendacao": "Recomendação da loja ou do produto",
}


# Como cada tema aparece na voz do cliente. Usado para expandir perguntas amplas
# ("quais os principais problemas?") em sub-buscas, uma por tema frequente no recorte.
THEME_QUERIES = {
    "entrega_atrasada": "entrega atrasada, demorou muito para chegar, fora do prazo",
    "produto_nao_recebido": "não recebi o produto, ainda não chegou",
    "entrega_incompleta": "pedido incompleto, veio faltando item, recebi só uma parte",
    "entrega_no_prazo": "entrega rápida, chegou antes do prazo",
    "produto_com_defeito": "produto veio com defeito, quebrado, não funciona",
    "produto_errado": "veio produto errado, diferente do anunciado",
    "qualidade_baixa": "produto de má qualidade, material ruim",
    "qualidade_boa": "produto de ótima qualidade, muito bom",
    "atendimento": "atendimento, entrei em contato e não tive resposta",
    "devolucao_reembolso": "quero devolver, trocar, cancelar e receber o dinheiro de volta",
    "recomendacao": "recomendo a loja e o produto",
}
POSITIVE_THEMES = frozenset({"entrega_no_prazo", "qualidade_boa", "recomendacao"})


def detect_themes(text_norm: str) -> list[str]:
    """Temas encontrados em um texto já normalizado (ver text.normalize)."""
    found = [name for name, pattern in THEME_PATTERNS.items() if pattern.search(text_norm)]
    # "não chegou no prazo" casa com "no prazo": é atraso, não elogio.
    if "entrega_no_prazo" in found and _NEG_PRAZO.search(text_norm):
        found.remove("entrega_no_prazo")
        if "entrega_atrasada" not in found:
            found.append("entrega_atrasada")
    return found
