"""Etapa 5 — construção do contexto e geração da resposta fundamentada.

O modelo só enxerga as avaliações recuperadas, numeradas, e deve citar [n] em cada
afirmação. Depois da geração, as citações são validadas contra o contexto: referência
inexistente é removida e resposta sem nenhuma citação válida é descartada.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

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
5. Se as avaliações não tratarem do que foi perguntado, se forem insuficientes ou se a pergunta \
estiver fora do escopo (avaliações de clientes de e-commerce), comece a resposta exatamente com \
"{NO_EVIDENCE_TAG}:" e explique em uma frase o que faltou. Não tente responder mesmo assim.
6. Se as evidências só cobrirem parte da pergunta, responda essa parte e diga explicitamente \
o que não foi possível sustentar.
7. Português do Brasil, direto, no máximo ~200 palavras, em tópicos curtos."""

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


def build_context(question: str, evidences: list[Evidence], stats: dict, filters: dict) -> str:
    """Mensagem de usuário enviada ao LLM: pergunta + panorama + evidências numeradas."""
    blocks = "\n\n".join(format_evidence(ev) for ev in evidences)
    return (
        f"PERGUNTA: {question}\n\n"
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


def _extractive_answer(evidences: list[Evidence]) -> str:
    """Resposta sem LLM: resume temas das evidências e lista os trechos, sem interpretar."""
    themes = Counter(t for ev in evidences for t in ev.temas)
    lines = [
        "_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das "
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


class Generator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.resolved_llm_provider()
        self._client = None
        if self.provider == "openai_compat":
            if not settings.llm_model:
                raise ValueError("Defina LLM_MODEL no .env (nome do modelo no seu provedor).")
            from openai import OpenAI

            self._client = OpenAI(
                api_key=settings.llm_api_key or "sem-chave",  # Ollama e afins ignoram a chave
                base_url=settings.llm_base_url,
            )
        elif self.provider != "extractive":
            raise ValueError(f"LLM_PROVIDER desconhecido: {self.provider!r}")

    def generate(self, context: str, evidences: list[Evidence]) -> Generation:
        if self.provider == "extractive":
            raw = _extractive_answer(evidences)
            model = "nenhum"
        else:
            completion = self._client.chat.completions.create(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
            )
            raw = completion.choices[0].message.content or ""
            model = self.settings.llm_model
        answer, status, cited, warnings = validate_answer(raw, len(evidences))
        return Generation(answer, status, cited, warnings, self.provider, model, raw)
