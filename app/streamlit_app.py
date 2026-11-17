"""Interface de exploração: streamlit run app/streamlit_app.py"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voc_rag.pipeline import RagPipeline  # noqa: E402

EXAMPLES = [
    "Quais são os principais problemas relatados pelos clientes?",
    "Quais reclamações relacionadas à entrega aparecem com maior frequência?",
    "O que os clientes mais elogiam em suas experiências de compra?",
    "Quais problemas são relatados por clientes insatisfeitos?",
    "O que os clientes mais elogiam na categoria beleza e saúde?",
    "Qual é a capital da França?",
]
DELIVERY_LABELS = {"no_prazo": "No prazo", "atrasada": "Atrasada", "nao_entregue": "Sem entrega registrada"}

st.set_page_config(page_title="Voz do Cliente — Olist", page_icon="🗣️", layout="wide")


@st.cache_resource(show_spinner="Carregando índice e modelos...")
def get_pipeline() -> RagPipeline:
    return RagPipeline()


try:
    pipeline = get_pipeline()
except FileNotFoundError as error:
    st.error(f"{error}\n\nSiga o passo a passo do README para preparar a base e o índice.")
    st.stop()

retriever = pipeline.retriever

# ----------------------------------------------------------------- barra lateral
with st.sidebar:
    st.header("Filtros de metadados")
    st.caption("Opcionais. Somam-se aos filtros inferidos da pergunta e têm precedência sobre eles.")
    score_range = st.slider("Nota da avaliação", 1, 5, (1, 5))
    year = st.selectbox("Ano da compra", ["Todos", 2016, 2017, 2018])
    category = st.selectbox("Categoria do produto", ["Todas", *retriever.categories])
    delivery = st.multiselect(
        "Situação da entrega", list(DELIVERY_LABELS), format_func=DELIVERY_LABELS.get
    )
    top_k = st.slider("Avaliações no contexto (k)", 4, 20, pipeline.settings.top_k)

    st.divider()
    st.caption(
        f"**Base:** {retriever.manifest['documentos']:,} avaliações com texto  \n"
        f"**Embeddings:** {retriever.manifest['embedding_model']}  \n"
        f"**Geração:** {pipeline.generator.provider}"
        + (f" / {pipeline.settings.llm_model}" if pipeline.generator.provider != "extractive" else "")
        + f"  \n**Similaridade mínima:** {retriever.min_similarity}".replace(",", ".")
    )
    if pipeline.generator.provider == "extractive":
        st.warning("Sem LLM configurado: respostas em modo extrativo. Configure o `.env`.")

manual_filters: dict = {}
if score_range != (1, 5):
    manual_filters["review_score"] = {"gte": score_range[0], "lte": score_range[1]}
if year != "Todos":
    manual_filters["ano"] = int(year)
if category != "Todas":
    manual_filters["categoria"] = category
if delivery:
    manual_filters["entrega_status"] = delivery

# ----------------------------------------------------------------- pergunta
st.title("Voz do Cliente — Olist")
st.caption(
    "Pergunte em linguagem natural. As respostas são geradas apenas a partir das avaliações "
    "recuperadas, e cada afirmação cita as avaliações que a sustentam."
)

if "question" not in st.session_state:
    st.session_state.question = ""


def _set_question(text: str) -> None:
    st.session_state.question = text


columns = st.columns(3)
for i, example in enumerate(EXAMPLES):
    columns[i % 3].button(example, key=f"ex{i}", on_click=_set_question, args=(example,), width="stretch")

with st.form("ask"):
    question = st.text_input("Sua pergunta", key="question", placeholder="Ex.: o que os clientes dizem sobre atraso na entrega?")
    submitted = st.form_submit_button("Perguntar", type="primary")

if not (submitted or st.session_state.question):
    st.stop()
if not question.strip():
    st.info("Digite uma pergunta.")
    st.stop()

with st.spinner("Recuperando avaliações e gerando a resposta..."):
    result = pipeline.ask(question, manual_filters, top_k)

# ----------------------------------------------------------------- resposta
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Resposta")
    if result.status == "ok":
        st.markdown(result.answer)
    else:
        st.warning(result.answer)
        if result.refusal_stage == "recuperacao":
            st.caption(f"Recusa na recuperação, sem chamar o LLM. {result.refusal_reason}")
        else:
            st.caption("Recusa na geração: as avaliações recuperadas não sustentam uma resposta.")
        if result.coverage:
            st.markdown("**O que a base cobre:** " + " · ".join(f"{t['rotulo']} ({t['n']})" for t in result.coverage))
        if result.suggestions:
            st.markdown("**Perguntas que a base sabe responder:**")
            for i, suggestion in enumerate(result.suggestions):
                st.button(suggestion, key=f"sugestao-{i}", on_click=_set_question, args=(suggestion,))
    if result.retrieval.borderline:
        st.caption("Zona cinzenta de similaridade: o LLM confirmou se as avaliações tratam do assunto.")
    for warning in result.warnings:
        st.caption(f"⚠️ {warning}")

    st.subheader("Evidências")
    if not result.evidences:
        st.caption("Nenhuma avaliação foi enviada ao modelo.")
    only_cited = bool(result.cited_refs) and st.toggle("Mostrar só as avaliações citadas na resposta", value=False)
    for ev in result.evidences:
        cited = ev.ref in result.cited_refs
        if only_cited and not cited:
            continue
        with st.container(border=True):
            st.markdown(f"**[{ev.ref}]** {'★' * ev.review_score}{'☆' * (5 - ev.review_score)}" + ("  ·  citada na resposta" if cited else ""))
            st.write(f"“{ev.texto}”")
            delay = f" (+{ev.dias_atraso} dias)" if ev.entrega_status == "atrasada" and ev.dias_atraso else ""
            st.caption(
                f"{ev.data_compra} · {ev.categoria} · {ev.uf} · entrega: "
                f"{DELIVERY_LABELS.get(ev.entrega_status, ev.entrega_status)}{delay} · "
                f"similaridade {ev.similarity:.2f} · rank denso {ev.dense_rank or '—'} · "
                f"rank BM25 {ev.bm25_rank or '—'} · id `{ev.review_id}`"
            )

with right:
    st.subheader("Como chegamos aqui")
    r = result.retrieval
    st.markdown("**1. Transformação da pergunta**")
    st.code(result.parsed.search_text, language=None)
    for note in result.parsed.notes:
        st.caption(f"• {note}")
    if len(r.queries) > 1:
        st.caption("Pergunta ampla: expandida em sub-buscas pelos temas mais frequentes do recorte:")
        for sub_query in r.queries:
            st.caption(f"→ {sub_query}")
    st.markdown("**2. Filtros aplicados**")
    st.json(result.filters or {"filtros": "nenhum"}, expanded=True)

    st.markdown("**3. Recuperação híbrida**")
    funnel = st.columns(4)
    funnel[0].metric("Densa", r.n_dense)
    funnel[1].metric("BM25", r.n_bm25)
    funnel[2].metric("≥ limiar", r.n_above_threshold)
    funnel[3].metric("Contexto", len(result.evidences))
    st.caption(
        f"Similaridade máxima {r.max_similarity:.2f} · suporte {r.support_similarity:.2f} · "
        f"limiar {r.min_similarity:.2f} · tempos (ms): {result.timings_ms}"
    )

    stats = r.stats
    if stats.get("total"):
        st.markdown(f"**4. Panorama do recorte** — {stats['total']:,} avaliações, nota média {stats['nota_media']}".replace(",", "."))
        themes = pd.DataFrame(stats["temas"])
        if not themes.empty:
            st.dataframe(
                themes[["rotulo", "n", "pct"]].rename(columns={"rotulo": "Tema (palavras-chave)", "n": "Avaliações", "pct": "%"}),
                hide_index=True,
                width="stretch",
            )
        st.caption("Contagem aproximada por regras de palavras-chave; uma avaliação pode ter vários temas.")

    if result.context:
        with st.expander("5. Contexto enviado ao modelo"):
            st.text(result.context)
