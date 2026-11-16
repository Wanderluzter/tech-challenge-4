"""Etapa 3 — transformação da pergunta.

A pergunta vira duas coisas:
1. um texto de busca focado no assunto (que será vetorizado e tokenizado para o BM25);
2. filtros de metadados extraídos por regras ("self-querying" determinístico).

Foco no assunto: gestores perguntam em linguagem analítica ("quais padrões recorrentes
aparecem nas avaliações relacionadas a...") e clientes escrevem em linguagem de relato
("não recebi meu produto"). As palavras analíticas não existem nas avaliações e só puxam
o vetor da pergunta para longe delas; por isso são removidas do texto de busca. A pergunta
original, intacta, é a que vai para o LLM.

Optamos por regras em vez de um LLM para extrair filtros: é gratuito, instantâneo,
reproduzível e cada filtro aplicado aparece no rastro mostrado ao usuário. As regras são
conservadoras — só filtram quando a pergunta delimita um grupo ("clientes insatisfeitos",
"nota 1", "em 2018", "principais problemas"). Perguntas abertas ("o que dizem sobre a
embalagem?") ficam sem filtro, para a busca semântica decidir. Todo filtro inferido é
exibido e pode ser sobrescrito pelos filtros manuais da interface.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .text import clean_text, normalize

Filters = dict[str, object]

# Apelidos de uso comum -> categoria oficial da base
CATEGORY_ALIASES = {
    "beleza": "beleza_saude",
    "saude": "beleza_saude",
    "informatica": "informatica_acessorios",
    "moveis": "moveis_decoracao",
    "decoracao": "moveis_decoracao",
    "esporte": "esporte_lazer",
    "esportes": "esporte_lazer",
    "relogios": "relogios_presentes",
    "relogio": "relogios_presentes",
    "utilidades domesticas": "utilidades_domesticas",
    "ferramentas": "ferramentas_jardim",
    "jardim": "ferramentas_jardim",
    "pet": "pet_shop",
    "bebes": "bebes",
    "brinquedos": "brinquedos",
    "telefonia": "telefonia",
    "celulares": "telefonia",
    "automotivo": "automotivo",
    "perfumaria": "perfumaria",
    "eletronicos": "eletronicos",
    "eletrodomesticos": "eletrodomesticos",
    "papelaria": "papelaria",
    "cama mesa e banho": "cama_mesa_banho",
    "cama mesa banho": "cama_mesa_banho",
}

# Vocabulário analítico da pergunta, que não descreve o assunto procurado
META_WORDS = frozenset(
    """qual quais que quem como onde quando quanto quantos quantas o a os as um uma de do da dos das
    em no na nos nas por pelo pela pelos pelas para com e ou se sao foi ser e ha existe existem
    principais principal cliente clientes consumidor consumidores avaliacao avaliacoes comentario
    comentarios relatam relatado relatados relatada relatadas relato relatos aparece aparecem
    padrao padroes recorrente recorrentes relacionado relacionados relacionada relacionadas tema
    temas frequencia maior mais sustentam sustenta conclusao podem pode identificado identificados
    sobre dizem falam acham suas seus sua seu determinadas determinados base nota notas
    aspectos aspecto quando tem""".split()
)

# Palavras que indicam a polaridade pedida, mas nenhum assunto específico. Se o texto de
# busca só tem palavras daqui, a pergunta é "ampla" e a recuperação a expande por temas.
GENERIC_WORDS = frozenset(
    """problema problemas reclamacao reclamacoes reclamam queixa queixas critica criticas defeitos
    elogio elogios elogiam elogiados elogiadas insatisfeito insatisfeitos insatisfacao satisfeito
    satisfeitos satisfacao experiencia experiencias compra compras baixa baixas alta altas negativa
    negativas positiva positivas gostam valorizam motivos motivo pontos fortes fracos""".split()
)

_LOW = re.compile(
    r"insatisfeit|nota(s)? (muito )?(baixa|ruim|ruins)|avaliac\w+ (negativ|ruins|ruim|baix)"
    r"|(pior|piores) (nota|avaliac)|clientes (descontentes|frustrados)|detratores"
)
_HIGH = re.compile(
    r"(?<!in)satisfeit|nota(s)? (muito )?(alta|boa|boas|maxima)|avaliac\w+ (positiv|boas|alta)"
    r"|elogi|(melhor|melhores) (nota|avaliac)|promotores"
)
# Pergunta sobre "problemas"/"reclamações" (no plural, como objeto da pergunta): exclui notas 4
# e 5. Sem isso, a busca por "problemas" traz elogios como "sem problemas, recomendo".
_COMPLAINTS = re.compile(r"\b(problemas|reclamacoes|queixas|criticas|defeitos)\b")
_EXPLICIT_SCORE = re.compile(r"(?:nota|notas) (\d)(?: (?:e|ou|a) (\d))?|\b(\d) estrelas?")
_YEAR = re.compile(r"\b(2016|2017|2018)\b")
_BAD_DELIVERY = re.compile(
    r"entreg\w+ (atrasad|com atraso|insatisfat|problemat|ruins|ruim|fora do prazo)"
    r"|pedidos? (que )?(atras|com atraso)|que (atrasaram|chegaram (com atraso|atrasad|depois do prazo))"
)
_NOT_DELIVERED = re.compile(r"pedidos? (que )?nao (foram |foi )?(entreg|cheg)|pedidos? nao entregues?")


@dataclass
class ParsedQuery:
    original: str
    search_text: str
    filters: Filters = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)  # explicação de cada transformação
    broad: bool = False  # pergunta sem assunto específico ("quais os principais problemas?")


def _detect_category(norm: str, categories: list[str]) -> tuple[str, str] | None:
    """Retorna (categoria, trecho da pergunta que a identificou)."""
    # "beleza e saúde" deve casar com "beleza_saude"
    padded = " " + " ".join(tok for tok in norm.split() if tok != "e") + " "
    # nome oficial por extenso ("beleza saude", "cama mesa banho"), do mais longo ao mais curto
    for category in sorted(categories, key=len, reverse=True):
        phrase = category.replace("_", " ")
        if category != "desconhecida" and f" {phrase} " in padded:
            return category, phrase
    for alias, category in sorted(CATEGORY_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if f" {alias} " in padded and category in categories:
            return category, alias
    return None


def focus_text(norm: str) -> str:
    """Remove o vocabulário analítico de uma pergunta já normalizada."""
    return " ".join(tok for tok in norm.split() if tok not in META_WORDS and not tok.isdigit())


def parse_query(
    question: str, categories: list[str] | None = None, focus: bool = True
) -> ParsedQuery:
    cleaned = clean_text(question)
    norm = normalize(cleaned)
    parsed = ParsedQuery(original=question, search_text=cleaned)
    focused = focus_text(norm) if focus else ""
    if focused and focused != norm:
        parsed.search_text = focused
        parsed.notes.append(f"texto de busca focado no assunto → “{focused}”")

    explicit = _EXPLICIT_SCORE.search(norm)
    if explicit:
        values = sorted(int(v) for v in explicit.groups() if v and 1 <= int(v) <= 5)
        if values:
            parsed.filters["review_score"] = {"gte": values[0], "lte": values[-1]}
            parsed.notes.append(f"nota explícita na pergunta → nota entre {values[0]} e {values[-1]}")
    elif _LOW.search(norm):
        parsed.filters["review_score"] = {"gte": 1, "lte": 2}
        parsed.notes.append("pergunta delimita clientes insatisfeitos / nota baixa → nota 1 ou 2")
    elif _COMPLAINTS.search(norm) and not _HIGH.search(norm):
        parsed.filters["review_score"] = {"gte": 1, "lte": 3}
        parsed.notes.append("pergunta sobre problemas/reclamações → exclui notas 4 e 5")
    elif _HIGH.search(norm):
        parsed.filters["review_score"] = {"gte": 4, "lte": 5}
        parsed.notes.append("pergunta delimita elogios / clientes satisfeitos → nota 4 ou 5")

    year = _YEAR.search(norm)
    if year:
        parsed.filters["ano"] = int(year.group(1))
        parsed.notes.append(f"ano citado → compras de {year.group(1)}")

    if _NOT_DELIVERED.search(norm):
        parsed.filters["entrega_status"] = ["nao_entregue"]
        parsed.notes.append("pedidos não entregues → sem data de entrega registrada")
    elif _BAD_DELIVERY.search(norm):
        parsed.filters["entrega_status"] = ["atrasada", "nao_entregue"]
        parsed.notes.append(
            "entrega insatisfatória → pedidos entregues após o prazo ou sem entrega registrada"
        )

    if categories:
        detected = _detect_category(norm, categories)
        if detected:
            category, phrase = detected
            parsed.filters["categoria"] = category
            parsed.notes.append(f"categoria citada → {category}")
            if focus:
                # a categoria já virou filtro; no texto de busca ela só atrairia avaliações
                # que citam a palavra, em vez das que respondem à pergunta
                drop = set(phrase.split()) | {"categoria", "categorias", "produtos", "produto"}
                rest = " ".join(t for t in parsed.search_text.split() if t not in drop)
                if rest:
                    parsed.search_text = rest
                    parsed.notes[0] = f"texto de busca focado no assunto → “{rest}”"

    tokens = normalize(parsed.search_text).split()
    parsed.broad = bool(tokens) and all(tok in GENERIC_WORDS or tok in META_WORDS for tok in tokens)

    if not parsed.filters:
        parsed.notes.append("nenhum filtro inferido: busca em toda a base")
    return parsed


def merge_filters(inferred: Filters, manual: Filters | None) -> Filters:
    """Filtros escolhidos na interface têm precedência sobre os inferidos da pergunta."""
    merged = dict(inferred)
    merged.update({k: v for k, v in (manual or {}).items() if v not in (None, "", [])})
    return merged


def to_chroma_where(filters: Filters) -> dict | None:
    clauses: list[dict] = []
    for key, value in filters.items():
        if isinstance(value, dict):  # intervalo
            if "gte" in value:
                clauses.append({key: {"$gte": value["gte"]}})
            if "lte" in value:
                clauses.append({key: {"$lte": value["lte"]}})
        elif isinstance(value, (list, tuple)):
            clauses.append({key: {"$in": list(value)}})
        else:
            clauses.append({key: value})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def to_mask(filters: Filters, docs):
    """Mesma semântica de to_chroma_where, como máscara booleana sobre o DataFrame."""
    import numpy as np

    mask = np.ones(len(docs), dtype=bool)
    for key, value in filters.items():
        column = docs[key]
        if isinstance(value, dict):
            if "gte" in value:
                mask &= (column >= value["gte"]).to_numpy()
            if "lte" in value:
                mask &= (column <= value["lte"]).to_numpy()
        elif isinstance(value, (list, tuple)):
            mask &= column.isin(list(value)).to_numpy()
        else:
            mask &= (column == value).to_numpy()
    return mask
