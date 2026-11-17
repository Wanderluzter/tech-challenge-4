"""Etapa 5 — construção do contexto e geração da resposta fundamentada.

O modelo só enxerga as avaliações recuperadas, numeradas, e deve citar [n] em cada
afirmação. Depois da geração, as citações são validadas contra o contexto: referência
inexistente é removida e resposta sem nenhuma citação válida é descartada.

A chamada ao LLM é uma chain LCEL do LangChain: `ChatPromptTemplate | ChatOpenAI |
StrOutputParser`. `ChatOpenAI` fala com qualquer API compatível com OpenAI (Gemini,
OpenRouter, Ollama), então trocar de provedor é só mudar o .env.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from .config import Settings
from .retriever import Evidence
from .themes import THEME_LABELS

NO_EVIDENCE_TAG = "SEM_EVIDENCIA"

SYSTEM_PROMPT = f"""Você é um analista de Voz do Cliente de um e-commerce brasileiro. \
Responda a perguntas de gestores usando EXCLUSIVAMENTE as avaliações de clientes fornecidas \
no contexto.

Regras:
1. Use apenas o que está no bloco AVALIAÇÕES RECUPERADAS e no PANORAMA. Não use conhecimento \
externo nem invente fatos, números, produtos ou causas.
2. Toda afirmação deve terminar com a citação das avaliações que a sustentam, no formato [n] \
ou [n, m], usando os números do contexto. Não cite números que não existem.
3. Organize a resposta por temas ou padrões, do mais para o menos sustentado pelas evidências. \
Diga quando um ponto aparece em poucas avaliações.
4. As avaliações recuperadas são uma amostra dos comentários mais relevantes, não a base \
inteira: não extrapole percentuais a partir delas. Para falar de frequência, use somente os \
números do PANORAMA, deixando claro que é uma contagem aproximada por palavras-chave.
5. Se NENHUMA avaliação tratar do assunto perguntado, ou se a pergunta estiver fora do escopo \
(avaliações de clientes de e-commerce), comece a resposta exatamente com "{NO_EVIDENCE_TAG}:" e \
explique em uma frase o que faltou. Não tente responder mesmo assim.
6. Se algumas avaliações tratarem do assunto, mesmo que poucas ou só de parte da pergunta, \
responda com base nelas (não recuse): diga quantas sustentam cada ponto e explicite o que não \
foi possível sustentar.
7. Português do Brasil, direto, no máximo ~200 palavras, em tópicos curtos."""

PROMPT = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", "{context}")])

_DELIVERY = {"no_prazo": "no prazo", "atrasada": "atrasada", "nao_entregue": "sem entrega registrada"}
_CITATION = re.compile(r"\[(\d+(?:\s*(?:,|e)\s*\d+)*)\]")


@dataclass
class Generation:
    answer: str
    status: str  # "ok" | "sem_evidencia"
    cited_refs: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    raw: str = ""


def format_evidence(ev: Evidence) -> str:
    delivery = _DELIVERY.get(ev.entrega_status, ev.entrega_status)
    if ev.entrega_status == "atrasada" and ev.dias_atraso:
        delivery += f" ({ev.dias_atraso} dias após o prazo)"
    header = (
        f"[{ev.ref}] nota {ev.review_score}/5 | compra em {ev.data_compra or 'data desconhecida'} "
        f"| categoria: {ev.categoria} | entrega: {delivery}"
    )
    return f'{header}\n"{ev.texto}"'


def format_stats(stats: dict, filters: dict, max_themes: int = 8) -> str:
    if not stats or not stats.get("total"):
        return "PANORAMA: indisponível."
    scope = f"filtros aplicados: {filters}" if filters else "toda a base, sem filtros"
    lines = [
        f"PANORAMA ({scope}) — {stats['total']} avaliações com texto, nota média {stats['nota_media']}.",
        "Distribuição por nota: " + ", ".join(f"nota {k}: {v}" for k, v in stats["por_nota"].items()) + ".",
        "Temas detectados por palavras-chave (contagem aproximada; uma avaliação pode ter vários):",
    ]
    lines += [f"- {t['rotulo']}: {t['n']} ({t['pct']}%)" for t in stats["temas"][:max_themes]]
    return "\n".join(lines)


BORDERLINE_NOTE = (
    "ATENÇÃO: a similaridade entre a pergunta e as avaliações recuperadas é limítrofe. Antes de "
    "responder, confirme se as avaliações tratam de fato do assunto perguntado; se nenhuma tratar, "
    f"responda com {NO_EVIDENCE_TAG}."
)


def build_context(
    question: str, evidences: list[Evidence], stats: dict, filters: dict, borderline: bool = False
) -> str:
    """Mensagem de usuário enviada ao LLM: pergunta + panorama + evidências numeradas."""
    blocks = "\n\n".join(format_evidence(ev) for ev in evidences)
    note = f"{BORDERLINE_NOTE}\n\n" if borderline else ""
    return (
        f"PERGUNTA: {question}\n\n{note}"
        f"{format_stats(stats, filters)}\n\n"
        f"AVALIAÇÕES RECUPERADAS ({len(evidences)}, da mais para a menos relevante):\n\n{blocks}\n\n"
        "Responda seguindo as regras."
    )


def extract_citations(text: str) -> list[int]:
    refs: list[int] = []
    for group in _CITATION.findall(text):
        refs += [int(n) for n in re.findall(r"\d+", group)]
    return refs


def validate_answer(raw: str, n_evidences: int) -> tuple[str, str, list[int], list[str]]:
    """Checagem pós-geração. Retorna (resposta, status, refs citadas, avisos)."""
    text = raw.strip()
    if text.upper().startswith(NO_EVIDENCE_TAG):
        reason = text[len(NO_EVIDENCE_TAG) :].lstrip(": \n") or "As evidências não sustentam uma resposta."
        return reason, "sem_evidencia", [], []

    warnings: list[str] = []
    valid = set(range(1, n_evidences + 1))
    invalid = sorted(set(extract_citations(text)) - valid)
    if invalid:
        # remove só os números inexistentes, preservando as citações válidas do mesmo colchete
        def fix(match: re.Match) -> str:
            kept = [n for n in re.findall(r"\d+", match.group(1)) if int(n) in valid]
            return f"[{', '.join(kept)}]" if kept else ""

        text = _CITATION.sub(fix, text)
        warnings.append(f"Citações inexistentes removidas da resposta: {invalid}")

    cited = sorted(set(extract_citations(text)) & valid)
    if not cited:
        return (
            "O modelo gerou uma resposta sem citar nenhuma avaliação recuperada. Como não é "
            "possível rastrear as afirmações até as evidências, a resposta foi descartada.",
            "sem_evidencia",
            [],
            warnings + ["Resposta descartada por falta de citações válidas."],
        )
    return text, "ok", cited, warnings


def _extractive_answer(evidences: list[Evidence], reason: str = "sem LLM configurado") -> str:
    """Resposta sem LLM: resume temas das evidências e lista os trechos, sem interpretar."""
    themes = Counter(t for ev in evidences for t in ev.temas)
    lines = [
        f"_Modo extrativo ({reason}): os trechos abaixo são citações literais das "
        "avaliações recuperadas, sem síntese por modelo de linguagem._",
        "",
    ]
    if themes:
        lines.append(f"**Temas mais presentes nas {len(evidences)} avaliações recuperadas:**")
        for theme, _ in themes.most_common(5):
            refs = ", ".join(str(ev.ref) for ev in evidences if theme in ev.temas)
            lines.append(f"- {THEME_LABELS[theme]} [{refs}]")
        lines.append("")
    lines.append("**Avaliações mais relevantes:**")
    for ev in evidences[:5]:
        snippet = ev.texto if len(ev.texto) <= 180 else ev.texto[:177] + "..."
        lines.append(f'- "{snippet}" (nota {ev.review_score}) [{ev.ref}]')
    return "\n".join(lines)


def _describe_api_error(error: Exception) -> str:
    status = getattr(error, "status_code", None)
    if status == 429:
        return "limite de requisições do provedor atingido"
    if status in (401, 403):
        return "chave de API inválida ou sem permissão"
    if status:
        return f"erro {status} do provedor"
    return type(error).__name__


@dataclass
class ModelState:
    estado: str = "disponivel"  # "disponivel" | "sem_cota" | "erro"
    erro: str | None = None
    desde: float | None = None  # epoch da última falha


class Generator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.resolved_llm_provider()
        self.models: list[str] = []
        self.states: dict[str, ModelState] = {}
        self._chains: dict[str, Runnable] = {}
        if self.provider == "openai_compat":
            if not settings.llm_model:
                raise ValueError("Defina LLM_MODEL no .env (nome do modelo no seu provedor).")
            self.models = settings.llm_models
            self.states = {m: ModelState() for m in self.models}
        elif self.provider != "extractive":
            raise ValueError(f"LLM_PROVIDER desconhecido: {self.provider!r}")

    # ------------------------------------------------------------ chains LCEL
    def _chat_model(self, model: str) -> Runnable:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            api_key=self.settings.llm_api_key or "sem-chave",  # Ollama e afins ignoram a chave
            base_url=self.settings.llm_base_url,
            temperature=self.settings.llm_temperature,
            timeout=self.settings.llm_timeout_s,
            max_retries=0,  # quem decide repetir ou trocar de modelo é a cadeia de fallback abaixo
        )

    def chain(self, model: str) -> Runnable:
        """prompt | LLM | parser — uma chain por modelo, criada na primeira chamada."""
        if model not in self._chains:
            self._chains[model] = (PROMPT | self._chat_model(model) | StrOutputParser()).with_config(
                run_name=f"gerar:{model}"
            )
        return self._chains[model]

    # ------------------------------------------------------------ estado dos modelos
    def _cooling(self, model: str) -> bool:
        """Modelo que falhou há pouco fica fora da fila até o fim do cooldown."""
        import time

        state = self.states.get(model)
        return bool(
            state and state.estado != "disponivel" and state.desde
            and time.time() - state.desde < self.settings.llm_cooldown_s
        )

    def model_status(self) -> list[dict]:
        return [
            {
                "modelo": m,
                "estado": s.estado if self._cooling(m) else "disponivel",
                "erro": s.erro if self._cooling(m) else None,
                "desde": s.desde if self._cooling(m) else None,
                "principal": i == 0,
            }
            for i, (m, s) in enumerate(self.states.items())
        ]

    def _mark(self, model: str, error: Exception | None) -> None:
        import time

        state = self.states.setdefault(model, ModelState())
        if error is None:
            state.estado, state.erro, state.desde = "disponivel", None, None
        else:
            state.estado = "sem_cota" if getattr(error, "status_code", None) == 429 else "erro"
            state.erro, state.desde = _describe_api_error(error), time.time()

    def _chain(self, model: str | None, allow_fallback: bool) -> list[str]:
        if not self.models:
            return [self.settings.llm_model]
        first = model if model in self.models else self.models[0]
        if not allow_fallback:
            return [first]
        rest = [m for m in self.models if m != first]
        # modelos em cooldown vão para o fim: só são tentados se nenhum outro responder
        return [first, *[m for m in rest if not self._cooling(m)], *[m for m in rest if self._cooling(m)]]

    # ------------------------------------------------------------ geração
    def generate(
        self, context: str, evidences: list[Evidence], model: str | None = None, allow_fallback: bool = True
    ) -> Generation:
        if self.provider == "extractive":
            raw = _extractive_answer(evidences)
            answer, status, cited, warnings = validate_answer(raw, len(evidences))
            return Generation(answer, status, cited, warnings, self.provider, "nenhum", raw)

        from openai import APIError

        chain = self._chain(model, allow_fallback)
        failures: list[str] = []
        for candidate in chain:
            if candidate != chain[0] and self._cooling(candidate) and candidate != chain[-1]:
                continue  # em cooldown e ainda há outras opções
            try:
                raw = self.chain(candidate).invoke({"context": context}) or ""
            except APIError as error:
                self._mark(candidate, error)
                failures.append(f"{candidate}: {_describe_api_error(error)}")
                continue
            self._mark(candidate, None)
            answer, status, cited, warnings = validate_answer(raw, len(evidences))
            if candidate != chain[0]:
                warnings.insert(
                    0, f"{chain[0]} indisponível ({failures[0].split(': ', 1)[1]}); resposta gerada por {candidate}."
                )
            return Generation(answer, status, cited, warnings, self.provider, candidate, raw)

        # nenhum modelo respondeu: mostra as evidências em vez de quebrar
        answer, status, cited, warnings = validate_answer(
            _extractive_answer(evidences, "LLM indisponível"), len(evidences)
        )
        reason = failures[0].split(": ", 1)[1] if len(failures) == 1 else "; ".join(failures)
        warnings.append(f"LLM indisponível ({reason}); exibindo as evidências recuperadas.")
        return Generation(answer, status, cited, warnings, "extractive_fallback", "nenhum", "")
