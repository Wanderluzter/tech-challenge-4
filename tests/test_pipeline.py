from __future__ import annotations

import pandas as pd
import pytest

from voc_rag import data_prep
from voc_rag.generator import NO_EVIDENCE_TAG, build_context, validate_answer
from voc_rag.pipeline import RagPipeline
from voc_rag.query import merge_filters, parse_query, to_chroma_where, to_mask
from voc_rag.text import clean_text, normalize, tokenize
from voc_rag.themes import detect_themes

CATEGORIES = ["beleza_saude", "cama_mesa_banho", "informatica_acessorios", "relogios_presentes"]


# ---------------------------------------------------------------- texto e temas
def test_clean_text_handles_missing_and_whitespace():
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""
    assert clean_text("  Muito   bom\r\nrecomendo  ") == "Muito bom recomendo"
    assert clean_text("ótimoooooo") == "ótimoo"


def test_normalize_and_tokenize_keep_negation():
    assert normalize("Não RECEBI, até hoje!") == "nao recebi ate hoje"
    assert "nao" in tokenize("Não recebi o produto")
    assert "o" not in tokenize("Não recebi o produto")


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Não recebi meu produto até hoje", "produto_nao_recebido"),
        ("A entrega atrasou muito", "entrega_atrasada"),
        ("Chegou antes do prazo", "entrega_no_prazo"),
        ("Veio com defeito", "produto_com_defeito"),
        ("Comprei dois e só veio um", "entrega_incompleta"),
    ],
)
def test_detect_themes(text, expected):
    assert expected in detect_themes(normalize(text))


def test_negated_deadline_is_delay_not_praise():
    themes = detect_themes(normalize("O pedido não chegou no prazo"))
    assert "entrega_no_prazo" not in themes
    assert "entrega_atrasada" in themes


# ---------------------------------------------------------------- preparação
def test_build_documents_selection_rules(raw):
    docs, report = data_prep.build_documents(raw, min_chars=10)
    ids = set(docs["review_id"])
    assert "vazio" not in ids  # sem texto
    assert "curto" not in ids  # texto sem conteúdo
    assert docs["review_id"].is_unique  # review_id duplicado removido
    assert report["sem_texto_descartadas"] == 1
    assert report["review_id_duplicado_descartadas"] == 1
    assert report["texto_curto_descartadas"] == 1
    assert report["documentos_na_base"] == len(docs)


def test_build_documents_metadata_and_missing_values(raw):
    docs, _ = data_prep.build_documents(raw)
    by_id = docs.set_index("review_id")
    # pedido inexistente: metadados ausentes viram categorias explícitas
    orphan = by_id.loc["orfao"]
    assert orphan["categoria"] == "desconhecida"
    assert orphan["entrega_status"] == "nao_entregue"
    assert pd.isna(orphan["dias_atraso"])
    assert "\n" not in orphan["texto"] and "  " not in orphan["texto"]
    assert set(docs["entrega_status"]) == {"no_prazo", "atrasada", "nao_entregue"}
    late = docs[docs["entrega_status"] == "atrasada"]
    assert (late["dias_atraso"] > 0).all()
    assert set(docs["sentimento"]) == {"negativo", "neutro", "positivo"}
    assert not docs[["texto", "categoria", "uf", "temas"]].isna().any().any()


def test_title_is_joined_to_comment(raw):
    docs, _ = data_prep.build_documents(raw)
    assert docs["texto"].str.startswith("Recomendo. ").any()


# ---------------------------------------------------------------- pergunta
def test_parse_open_question_has_no_filters():
    parsed = parse_query("O que os clientes dizem sobre a embalagem dos produtos?", CATEGORIES)
    assert parsed.filters == {}
    assert parsed.search_text == "embalagem produtos"


def test_complaint_question_excludes_high_scores():
    parsed = parse_query("Quais são os principais problemas relatados pelos clientes?", CATEGORIES)
    assert parsed.filters == {"review_score": {"gte": 1, "lte": 3}}
    # "quando têm um problema" não delimita reclamações: relatos de solução também interessam
    assert parse_query("Como avaliam o atendimento quando têm um problema?", CATEGORIES).filters == {}


@pytest.mark.parametrize(
    "question,expected",
    [
        ("Quais problemas são relatados por clientes insatisfeitos?", {"review_score": {"gte": 1, "lte": 2}}),
        ("O que os clientes mais elogiam?", {"review_score": {"gte": 4, "lte": 5}}),
        ("O que dizem as avaliações com nota 3?", {"review_score": {"gte": 3, "lte": 3}}),
        ("Problemas nas avaliações de nota 1 e 2 em 2018", {"review_score": {"gte": 1, "lte": 2}, "ano": 2018}),
        (
            "O que os clientes elogiam na categoria beleza e saúde?",
            {"review_score": {"gte": 4, "lte": 5}, "categoria": "beleza_saude"},
        ),
        (
            "Quais temas aparecem em experiências de entrega insatisfatórias?",
            {"entrega_status": ["atrasada", "nao_entregue"]},
        ),
    ],
)
def test_parse_infers_filters(question, expected):
    assert parse_query(question, CATEGORIES).filters == expected


def test_category_words_leave_search_text():
    parsed = parse_query("O que os clientes elogiam na categoria beleza e saúde?", CATEGORIES)
    assert "beleza" not in parsed.search_text and "saude" not in parsed.search_text


def test_focus_can_be_disabled():
    question = "Quais são os principais problemas relatados pelos clientes?"
    assert parse_query(question, CATEGORIES, focus=False).search_text == question


def test_manual_filters_take_precedence():
    merged = merge_filters({"ano": 2017, "categoria": "telefonia"}, {"ano": 2018, "categoria": ""})
    assert merged == {"ano": 2018, "categoria": "telefonia"}


def test_filters_translate_consistently(settings):
    docs = pd.read_parquet(settings.documents_path)
    filters = {"review_score": {"gte": 1, "lte": 2}, "entrega_status": ["atrasada"], "ano": 2018}
    where = to_chroma_where(filters)
    assert {"review_score": {"$gte": 1}} in where["$and"]
    assert {"entrega_status": {"$in": ["atrasada"]}} in where["$and"]
    subset = docs[to_mask(filters, docs)]
    assert len(subset) and (subset["review_score"] <= 2).all() and (subset["ano"] == 2018).all()
    assert to_chroma_where({}) is None


# ---------------------------------------------------------------- geração (validação)
def test_validate_accepts_grounded_answer():
    text, status, cited, warnings = validate_answer("Atraso é recorrente [1, 3]. Defeito aparece [2].", 3)
    assert status == "ok" and cited == [1, 2, 3] and not warnings


def test_validate_strips_nonexistent_citations():
    text, status, cited, warnings = validate_answer("Atraso [1, 9]. Outro ponto [7].", 3)
    assert status == "ok" and cited == [1]
    assert "[1]" in text and "9" not in text and "[7]" not in text
    assert warnings


def test_validate_discards_answer_without_citations():
    _, status, cited, warnings = validate_answer("Os clientes adoram tudo, sem dúvida.", 3)
    assert status == "sem_evidencia" and cited == [] and warnings


def test_validate_respects_model_refusal():
    text, status, _, _ = validate_answer(f"{NO_EVIDENCE_TAG}: as avaliações não falam disso.", 5)
    assert status == "sem_evidencia" and text == "as avaliações não falam disso."


# ---------------------------------------------------------------- ponta a ponta
@pytest.fixture(scope="module")
def pipeline(settings) -> RagPipeline:
    return RagPipeline(settings)


def test_answer_is_grounded_in_retrieved_reviews(pipeline):
    result = pipeline.ask("Os clientes reclamam de produto que veio quebrado ou com defeito?")
    assert result.status == "ok"
    assert 3 <= len(result.evidences) <= pipeline.settings.top_k
    assert any("defeito" in ev.texto for ev in result.evidences)
    assert result.cited_refs and set(result.cited_refs) <= {ev.ref for ev in result.evidences}
    assert all(ev.similarity >= pipeline.retriever.min_similarity for ev in result.evidences)
    for ev in result.evidences:  # o contexto enviado contém exatamente as evidências exibidas
        assert f"[{ev.ref}]" in result.context and ev.texto in result.context


def test_evidences_are_diverse(pipeline):
    result = pipeline.ask("entrega atrasada do pedido")
    texts = [normalize(ev.texto) for ev in result.evidences]
    assert len(texts) == len(set(texts))


def test_inferred_filter_restricts_evidences(pipeline):
    result = pipeline.ask("Clientes insatisfeitos reclamam de entrega atrasada?")
    assert result.filters["review_score"] == {"gte": 1, "lte": 2}
    assert result.evidences and all(ev.review_score <= 2 for ev in result.evidences)
    assert result.retrieval.stats["total"] == sum(result.retrieval.stats["por_nota"].values())


def test_manual_filter_restricts_evidences(pipeline):
    result = pipeline.ask("entrega atrasada do pedido", {"uf": "SP"})
    assert result.evidences and {ev.uf for ev in result.evidences} == {"SP"}


def test_out_of_scope_question_is_refused_without_llm(pipeline, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("o gerador não deve ser chamado sem evidência suficiente")

    monkeypatch.setattr(pipeline.generator, "generate", fail)
    result = pipeline.ask("Explique a teoria da relatividade de Einstein")
    assert result.status == "sem_evidencia"
    assert result.refusal_stage == "recuperacao"
    assert result.evidences == [] and result.context is None


def test_filters_without_matches_are_refused(pipeline):
    result = pipeline.ask("problemas na entrega", {"ano": 2016})
    assert result.status == "sem_evidencia" and "filtros" in result.refusal_reason


def test_model_refusal_is_propagated(pipeline, monkeypatch):
    """Pergunta do domínio sem resposta na base: a recuperação passa e o LLM recusa."""

    class FakeCompletions:
        def create(self, **kwargs):
            assert "AVALIAÇÕES RECUPERADAS" in kwargs["messages"][1]["content"]
            message = type("M", (), {"content": f"{NO_EVIDENCE_TAG}: nenhuma avaliação trata disso."})
            return type("C", (), {"choices": [type("Ch", (), {"message": message})]})

    fake_client = type("Client", (), {"chat": type("Chat", (), {"completions": FakeCompletions()})})
    monkeypatch.setattr(pipeline.generator, "provider", "openai_compat")
    monkeypatch.setattr(pipeline.generator, "_client", fake_client)
    result = pipeline.ask("Os clientes reclamam de produto com defeito?")
    assert result.status == "sem_evidencia" and result.refusal_stage == "geracao"
    assert result.cited_refs == [] and result.evidences  # evidências seguem visíveis para auditoria


def test_context_carries_metadata_and_panorama(pipeline):
    result = pipeline.ask("entrega atrasada do pedido")
    context = build_context("p", result.evidences, result.retrieval.stats, result.filters)
    assert "PANORAMA" in context and "nota" in context and "categoria:" in context


def test_broad_question_is_expanded_by_frequent_themes(pipeline):
    result = pipeline.ask("Quais são os principais problemas relatados pelos clientes?")
    assert result.parsed.broad and len(result.retrieval.queries) > 1
    assert result.status == "ok" and all(ev.review_score <= 3 for ev in result.evidences)
    # evidências cobrem mais de um tipo de problema, não só quem escreveu "problemas"
    assert len({theme for ev in result.evidences for theme in ev.temas}) >= 3


def test_specific_question_is_not_expanded(pipeline):
    result = pipeline.ask("Os clientes reclamam de produto com defeito?")
    assert not result.parsed.broad and len(result.retrieval.queries) == 1
