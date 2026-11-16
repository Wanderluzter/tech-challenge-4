# Plano — Tech Challenge Fase 4

Situação em 16/11/2026: **todos os requisitos técnicos estão prontos e medidos na base real**. Falta só o que depende da equipe: nomes e RMs, gravação do vídeo e envio na plataforma.

## Requisitos do enunciado

| Requisito | Situação | Onde |
|---|---|---|
| 1. Construção da base de conhecimento (seleção, limpeza, ausentes, organização, embeddings, indexação) | Pronto: 38.287 documentos indexados com `multilingual-e5-small` no ChromaDB | `data_prep.py`, `index.py`, README §4 |
| 2. Pipeline RAG (transformação, recuperação, seleção, contexto, geração) | Pronto: busca híbrida, RRF, MMR, panorama por temas e geração com LLM (Gemini) | `query.py`, `retriever.py`, `generator.py`, README §5 |
| 3. Respostas fundamentadas com evidências visíveis | Pronto: citações clicáveis, cartões de evidência, contexto enviado ao modelo | interface React, README §6 |
| 4. Perguntas sem evidência suficiente | Pronto e medido: 14/14 recusas corretas; 32/34 decisões corretas no total | README §6 e §8, Dashboard › Qualidade |
| Adicional: metadados | Pronto: nota, ano, categoria, situação da entrega e UF, inferidos ou manuais | README §7 |
| Entregável: repositório com README | Pronto, **faltam equipe e link do vídeo** no topo | `README.md` |
| Entregável: vídeo de até 7 min | Roteiro de 4:50 alinhado aos itens do enunciado e à apresentação (11 slides); **gravação pendente** | `docs/ROTEIRO_VIDEO.md` |

## O que falta

1. Preencher **nomes e RMs** no topo do README.
2. **Gravar o vídeo** seguindo `docs/ROTEIRO_VIDEO.md`. Deixe as perguntas abertas em abas antes (links `?q=` no roteiro): a geração leva de 10 a 40 s.
3. Subir o vídeo (YouTube não listado ou Drive com acesso por link) e colar o link no README.
4. Enviar na plataforma da FIAP o link do repositório e o do vídeo.
5. Bônus de +10 pontos: concluir a trilha *Generative AI Engineering Pathway* da Databricks Academy e enviar o certificado ou o print de *My Activities* com os cursos como *Completed*.

**Cota do LLM.** A camada gratuita do Gemini tem limite diário por modelo. Se a interface mostrar "LLM indisponível (limite de requisições)", espere a cota renovar ou troque `LLM_MODEL` no `.env` (por exemplo, `gemini-3.5-flash-lite`). Uma avaliação completa (`eval --e2e`) gasta até 34 chamadas; os exemplos, 8.

## Checklist dos critérios de avaliação

- [x] Recupera conteúdos relevantes — relevância@k média 0,78 nas 20 perguntas no escopo
- [x] Constrói contexto adequado — "Contexto enviado ao modelo" na interface
- [x] Respostas coerentes com as evidências — revisão manual do `docs/EXEMPLOS.md` (ressalva registrada no README §9)
- [x] Evita informações não fundamentadas — nenhuma resposta a pergunta que deveria ser recusada; validação de citações pós-geração
- [x] Rastreabilidade dos insights — citações `[n]` clicáveis, `review_id`, ranks vetorial e BM25
- [x] Reconhece falta de informação — 10/10 fora do escopo e 4/4 sem resposta na base
- [ ] Repositório claro e reproduzível — peça para alguém de fora seguir o README do zero

## Limitações conhecidas (README §11)

- Margem do limiar de apenas 0,001 entre perguntas no escopo e fora dele.
- Duas recusas indevidas no `eval`: reembolso (no limiar) e atendimento (recusada pelo LLM).
- Relevância medida por termos esperados, não por anotação humana.

## Se sobrar tempo

1. **Reranker** cross-encoder multilíngue sobre os candidatos do RRF — atacaria a margem do limiar.
2. **Anotar relevância** de ~50 pares pergunta–avaliação para medir precisão e recall reais.
3. **Verificador de fidelidade** (LLM-juiz): cada frase é sustentada pela avaliação citada?
