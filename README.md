# Voz do Cliente — RAG sobre as avaliações da Olist

Tech Challenge — Fase 4 (FIAP POSTECH). Solução de **Voice of Customer Intelligence**: gestores perguntam em linguagem natural e recebem respostas geradas **somente** a partir das avaliações de clientes do [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data), com as avaliações que sustentam cada afirmação exibidas ao lado. Quando não há evidência suficiente, o sistema diz que não sabe.

> **Equipe:** _preencher nomes e RMs_ · **Vídeo:** _preencher link_

## Sumário

1. [O problema](#1-o-problema)
2. [Arquitetura](#2-arquitetura)
3. [Como executar](#3-como-executar)
4. [Preparação da base de conhecimento](#4-preparação-da-base-de-conhecimento)
5. [Pipeline RAG](#5-pipeline-rag)
6. [Respostas fundamentadas e perguntas sem evidência](#6-respostas-fundamentadas-e-perguntas-sem-evidência)
7. [Metadados (desafio adicional)](#7-metadados-desafio-adicional)
8. [Avaliação](#8-avaliação)
9. [Exemplos de perguntas e respostas](#9-exemplos-de-perguntas-e-respostas)
10. [Decisões técnicas](#10-decisões-técnicas)
11. [Limitações e próximos passos](#11-limitações-e-próximos-passos)
12. [Estrutura do repositório](#12-estrutura-do-repositório)

## 1. O problema

A Olist tem cerca de 99 mil avaliações de pedidos feitos entre 2016 e 2018. A nota (1 a 5) diz *quanto* o cliente ficou satisfeito; o *porquê* está no comentário escrito, que ninguém consegue ler em escala. Esta solução transforma os comentários em uma base consultável para responder, com evidências, perguntas como:

- Quais são os principais problemas relatados pelos clientes?
- Quais reclamações relacionadas à entrega aparecem com maior frequência?
- O que os clientes mais elogiam?
- Quais avaliações sustentam a conclusão de que há problemas recorrentes de prazo?

## 2. Arquitetura

```mermaid
flowchart TD
    subgraph Ingestão ["Ingestão (offline, uma vez)"]
        A[CSVs da Olist<br/>reviews, orders, items,<br/>products, customers] --> B[Seleção e limpeza<br/>data_prep.py]
        B --> C[Documentos<br/>1 avaliação = 1 documento<br/>+ metadados + temas]
        C --> D[Embeddings<br/>multilingual-e5-small]
        D --> E[(ChromaDB<br/>HNSW, cosseno)]
        C --> F[(Parquet<br/>texto, metadados, BM25)]
    end

    subgraph Interface ["Interface"]
        W[React<br/>Perguntar + Dashboard] -- HTTP --> API[API FastAPI<br/>api.py]
    end

    subgraph Consulta ["Consulta (a cada pergunta)"]
        Q[Pergunta do usuário<br/>+ filtros manuais] --> T[Transformação<br/>foco no assunto +<br/>filtros inferidos]
        T --> X{Pergunta ampla?}
        X -- sim --> S[Sub-buscas pelos temas<br/>mais frequentes do recorte]
        X -- não --> R
        S --> R[Busca híbrida<br/>densa + BM25, com filtros]
        R --> U[Fusão RRF]
        U --> G{Evidência suficiente?<br/>≥ 3 avaliações acima<br/>do limiar de similaridade}
        G -- não --> N[Recusa<br/>LLM não é chamado]
        G -- sim --> M[Diversificação MMR<br/>top-k]
        M --> P[Contexto<br/>evidências numeradas<br/>+ panorama do recorte]
        P --> L[LLM<br/>responde citando n]
        L --> V{Citações válidas?}
        V -- não --> N2[Recusa / resposta descartada]
        V -- sim --> O[Resposta + evidências<br/>+ rastro do pipeline]
    end

    API --> Q
    O --> API
    N --> API
    N2 --> API
    E -.-> R
    F -.-> R
    F -.-> P
    F -.-> D2[(Métricas do<br/>dashboard)]
    D2 -.-> API
```

| Camada | Tecnologia | Papel |
|---|---|---|
| Dados | pandas, pyarrow | Junção, limpeza e base em Parquet |
| Embeddings | `intfloat/multilingual-e5-small` (sentence-transformers) | Vetores de 384 dimensões, multilíngue, roda em CPU |
| Banco vetorial | ChromaDB (persistente, HNSW, cosseno) | Busca densa com filtro de metadados |
| Busca lexical | rank-bm25 | Termos exatos; complementa a busca densa |
| Geração | Qualquer API compatível com OpenAI (OpenAI, Gemini, Groq, Ollama...) | Síntese com citações |
| Interface | React + Vite + Tailwind + Recharts, servida por FastAPI; Streamlit e CLI como alternativas | Perguntas com evidências e rastro do pipeline; dashboard de métricas |
| Testes | pytest | 46 testes, sem download de modelo nem chave de API |

## 3. Como executar

Requisitos: Python 3.10+ (testado em 3.12), Node 18+ para a interface React (testado em 22) e alguns GB de disco para as dependências (PyTorch), o modelo de embeddings e o índice.

```bash
git clone https://github.com/Wanderluzter/tech-challenge-4.git
cd tech-challenge-4
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

cp .env.example .env                 # configure o LLM (seção abaixo)

python scripts/download_data.py      # baixa os CSVs para data/raw/
python -m voc_rag.cli prepare        # CSVs → data/processed/documents.parquet
python -m voc_rag.cli index          # embeddings + ChromaDB (alguns minutos em CPU)
python -m voc_rag.cli eval --write   # calibra o limiar de similaridade (ver seção 8)

python -m voc_rag.cli ask "O que os clientes relatam sobre atraso na entrega?"
```

**Interface React (principal)** — requer Node 18+:

```bash
cd web && npm install && npm run build && cd ..   # gera web/dist
uvicorn voc_rag.api:app --port 8000               # interface + API em http://localhost:8000
```

Duas páginas: **Perguntar** (resposta com citações clicáveis, evidências, filtros de metadados e o rastro de cada etapa do pipeline) e **Dashboard**, com três abas — *Base de avaliações* (notas, temas, categorias, efeito do atraso na nota), *Uso do RAG* (perguntas feitas, taxa de recusa por etapa, tempo de resposta; registradas em `data/logs/perguntas.jsonl`, fora do git) e *Qualidade* (resultado do `eval`, incluindo onde o limiar separa perguntas no escopo e fora dele). `/?q=<pergunta>` abre a página já com a resposta. Para desenvolver o frontend com recarga automática: `make api` num terminal e `make web-dev` em outro (http://localhost:5173).

**Alternativa sem Node:** `streamlit run app/streamlit_app.py` abre a interface Streamlit, com as mesmas respostas e evidências (sem o dashboard).

Com `make`: `make setup data prepare index eval web` (ou `app` para o Streamlit).

**LLM.** Edite o `.env` com `LLM_API_KEY`, `LLM_MODEL` e, se não for a OpenAI, `LLM_BASE_URL`. Em `LLM_FALLBACK_MODELS` liste modelos alternativos do mesmo provedor (ex.: `gemini-3-flash-preview,gemini-3.5-flash-lite`): quando um modelo fica sem cota ou não responde em `LLM_TIMEOUT` segundos, a resposta é gerada pelo próximo e a interface avisa qual modelo respondeu. O cabeçalho da interface tem um seletor de modelo que mostra o estado de cada um (disponível, sem cota, com erro). A avaliação (`eval`) nunca troca de modelo no meio da medição. O `.env.example` traz os endpoints dos provedores mais comuns, inclusive Ollama local. Sem nenhuma chave, o sistema roda em **modo extrativo**: recupera e exibe as evidências, lista os temas, mas não sintetiza — útil para testar a recuperação sem custo.

**Sem acesso ao Hugging Face?** `EMBEDDING_BACKEND=lsa` usa um backend offline (TF-IDF de caracteres + SVD). É mais fraco e serve para testes; veja a seção 8.

**Dados.** O script tenta o Kaggle (via `kagglehub`) e, se falhar, o espelho público da própria Olist no GitHub. Também é possível baixar o zip do Kaggle manualmente e extrair em `data/raw/`.

**Testes:** `pytest` (usam uma base sintética mínima gerada no próprio teste).

## 4. Preparação da base de conhecimento

Código: [`src/voc_rag/data_prep.py`](src/voc_rag/data_prep.py). O funil abaixo é gravado em `data/processed/prep_report.json` a cada execução.

| Etapa | Avaliações | Decisão e justificativa |
|---|---|---|
| Arquivo original | 99.224 | — |
| Sem texto (título e comentário vazios) | −56.537 | **Descartadas.** Não há conteúdo a recuperar; preencher texto ausente seria fabricar evidência. A nota delas continua disponível nos dados brutos. |
| `review_id` repetido | −317 | A mesma avaliação aparece ligada a mais de um pedido. Fica uma linha por avaliação, para não inflar a evidência. |
| Texto sem conteúdo (menos de 10 caracteres úteis: "ok", "bom", "recomendo") | −4.083 | Não explicam nada e competiriam com evidências reais no top-k. |
| **Base de conhecimento** | **38.287** | |

- **Seleção dos dados.** O documento é `título + comentário` da avaliação. Dos demais arquivos entram apenas metadados do pedido (seção 7).
- **Limpeza.** Normalização Unicode, remoção de caracteres de controle, quebras de linha e espaços repetidos, e redução de letras repetidas ("ótimoooo"). Acentos e caixa são **preservados** no texto exibido e vetorizado: o modelo de embeddings lida com eles e o LLM lê melhor o texto original. Uma segunda versão (minúsculas, sem acento, sem pontuação) alimenta o BM25 e as regras. A lista de stopwords do BM25 mantém "não", "sem" e "nunca" de propósito — "recebi" e "não recebi" são avaliações opostas.
- **Valores ausentes.** Texto ausente: a avaliação sai da base. Metadado ausente (pedido sem categoria, sem data de entrega): vira categoria explícita (`desconhecida`, `nao_entregue`), nunca um valor imputado.
- **Organização dos documentos.** Uma avaliação = um documento, **sem chunking**. A mediana é de 59 caracteres e o comentário mais longo tem cerca de 200; dividir não traria ganho e quebraria a rastreabilidade "uma evidência = uma avaliação com `review_id`".
- **Textos repetidos.** Há 3.841 textos idênticos a outro ("Não recebi o produto"). Ficam na base, porque repetição é sinal de frequência, e são deduplicados na hora de montar o contexto.
- **Temas.** Cada avaliação recebe temas por regras de palavras-chave ([`themes.py`](src/voc_rag/themes.py)): entrega atrasada, produto não recebido, defeito, produto errado, atendimento etc. Servem para o panorama quantitativo e para expandir perguntas amplas (seção 5).
- **Embeddings e indexação.** Cada documento é vetorizado com o prefixo `passage: ` exigido pela família E5 e gravado no ChromaDB com os metadados filtráveis. O texto vetorizado é só o comentário — os metadados não são concatenados a ele, para não contaminar a semântica; eles atuam como filtro e como contexto para o LLM.

## 5. Pipeline RAG

Código: [`query.py`](src/voc_rag/query.py) → [`retriever.py`](src/voc_rag/retriever.py) → [`generator.py`](src/voc_rag/generator.py), orquestrados em [`pipeline.py`](src/voc_rag/pipeline.py). Cada etapa aparece no painel "Como chegamos aqui" da interface.

**1. Transformação da pergunta.**
- *Foco no assunto.* Gestores perguntam em linguagem analítica ("quais padrões recorrentes aparecem nas avaliações relacionadas a...") e clientes escrevem relatos ("não recebi meu produto"). O vocabulário analítico é removido do texto de busca: `"O que os clientes relatam sobre problemas relacionados à entrega?"` → `"problemas entrega"`. A pergunta original, intacta, é a que vai para o LLM.
- *Filtros inferidos.* Regras extraem filtros de metadados quando a pergunta delimita um grupo: "clientes insatisfeitos" → nota 1–2; "elogiam" → nota 4–5; "principais problemas" → exclui notas 4–5; "nota 3", "em 2018", "categoria beleza e saúde", "entregas insatisfatórias" → pedidos atrasados ou não entregues.
- *Perguntas amplas.* "Quais são os principais problemas?" não tem assunto para buscar — a palavra "problemas" só encontraria quem escreveu "problemas" (inclusive "sem problemas, recomendo"). Nesses casos a busca é decomposta em sub-buscas, uma para cada tema **mais frequente no recorte filtrado**, escritas na voz do cliente ("não recebi o produto, ainda não chegou").

**2. Recuperação semântica.** Busca densa no ChromaDB (cosseno, top 40, com os filtros) e busca lexical BM25 (top 40, mesmo recorte). A densa encontra paráfrases; o BM25 garante termos exatos que o embedding dilui.

**3. Seleção.** Os rankings são fundidos por **Reciprocal Rank Fusion**, que dispensa normalizar escalas de score diferentes. Candidatos abaixo da similaridade mínima saem; textos idênticos contam uma vez; e **MMR** (λ = 0,7) escolhe as 12 avaliações finais equilibrando relevância e diversidade — sem isso, o contexto vira doze variações de "não recebi".

**4. Construção do contexto.** O modelo recebe a pergunta, um **panorama quantitativo** do recorte (total de avaliações, distribuição de notas, temas por frequência) e as evidências numeradas com seus metadados:

```text
[3] nota 1/5 | compra em 2018-02-13 | categoria: moveis_quarto | entrega: sem entrega registrada
"Ja é as egunda vez que tenho problemas com entregas"
```

O panorama existe porque top-k recupera *exemplos*, não *contagens*: sem ele, "com maior frequência" seria um chute do modelo a partir de 12 avaliações.

**5. Geração.** O prompt de sistema ([`generator.py`](src/voc_rag/generator.py)) obriga a usar só o contexto, citar `[n]` em toda afirmação, não extrapolar percentuais das evidências e recusar com um marcador explícito quando elas não respondem à pergunta. Temperatura 0,1.

## 6. Respostas fundamentadas e perguntas sem evidência

**Rastreabilidade.** Toda resposta vem com as avaliações recuperadas: texto, nota, data, categoria, situação da entrega, similaridade, posição nos rankings denso e BM25, `review_id` e a marcação de quais foram citadas. O contexto exato enviado ao modelo também fica visível.

**Três barreiras contra respostas sem suporte:**

| # | Onde | O que faz | Cobre |
|---|---|---|---|
| 1 | Recuperação | Exige ao menos 3 avaliações distintas com similaridade ≥ limiar calibrado. Se não houver, **o LLM nem é chamado**. Filtros que não retornam nada também recusam aqui. | Pergunta fora do escopo ("capital da França"); recorte vazio |
| 2 | Geração | O modelo é instruído a responder `SEM_EVIDENCIA:` quando as avaliações recuperadas não tratam do que foi perguntado, e a declarar o que não conseguiu sustentar quando a cobertura é parcial. | Pergunta do domínio sem resposta na base ("bateria do iPhone 15") |
| 3 | Pós-geração | Citações a números inexistentes são removidas; resposta sem nenhuma citação válida é **descartada**. | Modelo que ignora as regras |

A recusa informa em que etapa ocorreu e por quê.

## 7. Metadados (desafio adicional)

| Metadado | Origem | Uso |
|---|---|---|
| `review_score`, `sentimento` | avaliações | Filtro (inferido ou manual) e contexto |
| `ano`, `data_compra` | pedidos | Filtro e contexto |
| `categoria` | itens → produtos (categoria do 1º item) | Filtro e contexto |
| `entrega_status`, `dias_atraso` | data de entrega × data prometida | Filtro e contexto |
| `uf` | clientes | Filtro manual e contexto |
| `temas` | regras sobre o texto | Panorama e expansão de perguntas amplas |

**Por que melhoram a recuperação.** (1) *Precisão:* "problemas nas avaliações com nota baixa" restringe a busca às 10,7 mil avaliações de nota 1–2 em vez de esperar que o embedding infira sentimento. (2) *Fato x relato:* `entrega_status` vem das datas do pedido, não do texto. "Entregas insatisfatórias" passa a significar pedidos que **de fato** atrasaram ou não chegaram — a nota média desses grupos é 1,88 e 1,48, contra 3,93 dos entregues no prazo. (3) *Contexto para o LLM:* cada evidência chega com nota, data e situação da entrega, o que permite conclusões como "as reclamações de atraso vêm de pedidos entregues após o prazo".

## 8. Avaliação

`python -m voc_rag.cli eval --write --e2e` roda [`eval/perguntas.json`](eval/perguntas.json): **20 perguntas no escopo** (todas as do enunciado + 6 da equipe: aplicativo, troca/devolução, reembolso, embalagem, cobrança/cancelamento e elogios em cama, mesa e banho), **10 fora do escopo** e **4 do domínio sem resposta na base** (bateria do iPhone 15, faturamento, Pix e cashback — os dois últimos têm zero menções nas 38.287 avaliações). Mede filtros inferidos, relevância@k por termos esperados (proxy auditável; não substitui julgamento humano) e a similaridade de suporte — a da 3ª melhor avaliação distinta —, usada para **calibrar o limiar** que separa o que responder do que recusar. `--write` grava o limiar no manifesto do índice; `--e2e` roda o pipeline completo e mostra qual barreira recusou cada pergunta.

### Resultados (configuração final)

Medidos em 16/11/2026 sobre a base real (38.287 avaliações), com `intfloat/multilingual-e5-small` e o LLM `gemini-3.5-flash` (API do Google, camada gratuita). Saída completa em [`eval/resultado.md`](eval/resultado.md); a aba *Qualidade* do dashboard lê a mesma execução. Uma rodada anterior com outro LLM, `nvidia/nemotron-3-ultra-550b-a55b:free` (via OpenRouter), deu o mesmo placar, 32/34, com os mesmos dois erros.

| Métrica | Backend offline (`lsa`), sem LLM, 25 perguntas | **e5 + Gemini, 34 perguntas** |
|---|---|---|
| Filtros inferidos corretamente | 22/22 | **30/30** |
| Relevância@k por termos (perguntas no escopo) | 0,74 | **0,78** |
| Aceitar/recusar só com o limiar — barreira 1 | 86% | **100%** (limiar calibrado: 0,875) |
| Decisão ponta a ponta (responder × recusar) | 18/25 | **32/34** |
| Perguntas fora do escopo recusadas | — | **10/10**, todas antes de chamar o LLM |
| Perguntas do domínio sem resposta recusadas | — | **4/4** (3 na recuperação, 1 pelo LLM) |

**Os dois erros, ambos recusas indevidas (nenhuma resposta sem fundamento):**

- *"Os clientes relatam problemas com reembolso ou estorno?"* — similaridade de suporte 0,875, exatamente sobre o limiar; no pipeline completo ficou um fio abaixo e foi recusada na recuperação.
- *"Como os clientes avaliam o atendimento quando têm um problema?"* — chegou ao LLM, que respondeu `SEM_EVIDENCIA`. As avaliações recuperadas falam de atendimento ruim, mas pouco de *como* o cliente avalia o atendimento diante de um problema; os dois modelos foram conservadores aqui (o Nemotron chegou a responder com 2 citações em uma execução e a recusar em outra).

**Leitura.** O sistema erra para o lado seguro: nas 34 perguntas não houve nenhuma resposta a pergunta que deveria ser recusada. O ponto frágil é a **margem do limiar**: o menor suporte no escopo foi 0,875 e o maior fora do escopo, 0,874 ("receita de bolo de cenoura"). Similaridades do E5 ficam comprimidas numa faixa alta, então perguntas novas podem cair do lado errado. Um reranker cross-encoder (seção 11) daria uma pontuação com mais separação.

Para reproduzir: `python -m voc_rag.cli eval --write --e2e` e `python -m voc_rag.cli examples`. Se o LLM ficar indisponível (limite de requisições), a avaliação tenta de novo e, persistindo a falha, marca a pergunta como `erro_llm` em vez de contá-la como respondida; o `examples` não sobrescreve o arquivo.

## 9. Exemplos de perguntas e respostas

[`docs/EXEMPLOS.md`](docs/EXEMPLOS.md) traz dez perguntas com transformação, filtros, funil de recuperação, resposta e evidências — saída real do sistema, sem edição. Foi gerado com o Nemotron (`nvidia/nemotron-3-ultra-550b-a55b:free`); a regeneração com o Gemini parou no limite diário da camada gratuita, e o comando não sobrescreve o arquivo nesse caso.

Trecho (pergunta ampla; resposta do LLM resumida, evidências literais):

> **Pergunta:** Quais são os principais problemas relatados pelos clientes?
> **Filtros inferidos:** nota entre 1 e 3 · **Expandida em sub-buscas:** produto não recebido · devolução/reembolso · entrega incompleta · entrega atrasada · produto com defeito
> **Recuperação:** 199 densos + 200 lexicais → 345 únicos → 262 acima do limiar → 12 no contexto
>
> - **Entrega incompleta / itens faltando** – 1.460 menções (10,4%); diversos relatos de pedidos com itens ausentes [2, 6, 7, 8].
> - **Produto com defeito ou danificado** – 988 menções (7,0%); produtos recebidos quebrados ou sem funcionar [1, 4, 5, 11].
>
> [2] nota 2 — “Pedido incompleto. Meu pedido chegou faltando um item.”
> [4] nota 1 — “Produto já veio com defeito não funciona”

> **Pergunta:** Qual é a capital da França?
> **Status:** sem evidência (recusa na recuperação, LLM não chamado) — 0 avaliações atingiram a similaridade mínima (maior encontrada: 0,82); mínimo exigido: 3.

**Revisão manual das respostas.** As afirmações conferem com as avaliações citadas. A ressalva mais relevante: no exemplo 1 o modelo agrupa [9] e [12] como "não recebimento", mas pelos metadados esses pedidos chegaram atrasados — é o tipo de deslize que a validação estrutural de citações não pega (seção 11).

## 10. Decisões técnicas

| Decisão | Alternativa considerada | Por quê |
|---|---|---|
| Uma avaliação = um documento, sem chunking | Chunks de tamanho fixo | Textos curtos; preserva a rastreabilidade por `review_id` |
| `multilingual-e5-small` | Modelos maiores; APIs de embedding | Feito para busca assimétrica em vários idiomas, gratuito e leve o bastante para rodar em CPU. Trocar o modelo é uma linha no `.env` |
| ChromaDB local | FAISS; serviço gerenciado | Persistência e filtro de metadados prontos, sem infraestrutura. Para 38 mil vetores, um serviço seria custo sem benefício |
| Híbrido denso + BM25 com RRF | Só busca densa | Comentários têm termos literais importantes ("nota fiscal", "correios"); RRF é robusto e não tem parâmetro sensível |
| Filtros por regras | LLM extraindo filtros (self-query) | Gratuito, instantâneo, reproduzível e auditável; cada filtro aparece no rastro e pode ser sobrescrito na interface |
| Expansão de perguntas amplas por temas frequentes | HyDE / multi-query por LLM | Guiada pelos dados do recorte, determinística e sem chamada extra ao modelo |
| Panorama quantitativo no contexto | Deixar o LLM estimar frequência | Top-k não conta; frequência precisa vir de agregação sobre a base |
| Temas por palavras-chave | Classificador / clustering | Transparente e barato. É aproximação e é apresentado como tal |
| MMR + deduplicação | Top-k puro | A base tem milhares de comentários quase idênticos |
| Recusa antes do LLM | Confiar só no prompt | Sem contexto não há o que alucinar, e não há custo |
| Validação de citações pós-geração | Confiar no modelo | Garante que toda resposta exibida aponta para evidências existentes |
| API compatível com OpenAI | SDK de um provedor | Um cliente só atende OpenAI, Gemini, Groq e Ollama |

## 11. Limitações e próximos passos

- **Margem estreita do limiar.** Com o e5-small, perguntas válidas e fora do escopo ficam separadas por 0,001 de similaridade de suporte (seção 8). Funciona no conjunto de avaliação, mas é sensível a perguntas novas.
- **LLM gratuito não determinístico e com cota diária.** A mesma pergunta pode ser respondida numa execução e recusada em outra, e a cota de um modelo pode acabar no meio do uso. A cadeia de fallback mantém a interface respondendo, mas modelos diferentes escrevem respostas diferentes; um modelo pago ou local, com temperatura 0, reduz a variação.
- **UF só por filtro manual.** "Clientes de São Paulo" não vira filtro automaticamente; o estado é selecionado na barra lateral.
- **Relevância medida por proxy.** Termos esperados não substituem um conjunto anotado por pessoas; anotar ~50 pares pergunta–avaliação permitiria medir precisão e recall de verdade.
- **Validação de citações é estrutural.** Garante que a citação existe, não que a avaliação citada sustenta a frase. Um verificador (NLI ou LLM-juiz) seria o próximo passo.
- **Temas por regras** têm falsos positivos e negativos; cerca de 36% das avaliações não recebem tema. As contagens são sempre apresentadas como aproximadas.
- **Regras de filtro** cobrem os padrões de pergunta mais comuns; formulações incomuns ficam sem filtro (a busca semântica ainda funciona, e os filtros manuais estão na interface).
- **Categoria do pedido** é a do primeiro item; pedidos com itens de categorias diferentes perdem essa nuance.
- **Sem reranker.** Um cross-encoder multilíngue sobre os candidatos do RRF tende a melhorar a ordenação, ao custo de latência.
- **Sem memória de conversa.** Cada pergunta é independente.

## 12. Estrutura do repositório

```text
├── web/                      # interface React (Vite + Tailwind + Recharts)
│   └── src/pages/            # Ask.tsx (perguntas) · Dashboard.tsx (métricas)
├── app/streamlit_app.py      # interface alternativa em Streamlit
├── src/voc_rag/
│   ├── config.py             # parâmetros (via .env)
│   ├── text.py               # limpeza e normalização
│   ├── themes.py             # taxonomia de temas por regras
│   ├── data_prep.py          # 1. CSVs → base de documentos
│   ├── embeddings.py         # backends de embedding (e5, lsa)
│   ├── index.py              # 2. embeddings → ChromaDB
│   ├── query.py              # 3. transformação da pergunta e filtros
│   ├── retriever.py          # 4. busca híbrida, RRF, limiar, MMR
│   ├── generator.py          # 5. contexto, prompt, validação de citações
│   ├── pipeline.py           # orquestração e rastro
│   ├── evaluation.py         # avaliação e calibração do limiar
│   ├── api.py                # API FastAPI (serve também web/dist)
│   ├── dashboard.py          # métricas da base, do uso e da avaliação
│   └── cli.py                # prepare | index | ask | eval | examples
├── scripts/download_data.py
├── eval/perguntas.json       # perguntas de avaliação  ·  eval/resultado.md e .json
├── tests/                    # pytest
├── docs/                     # EXEMPLOS.md · PLANO.md · ROTEIRO_VIDEO.md
└── data/                     # raw/, processed/, index/ (gerados; fora do git)
```

Os dados da Olist não são versionados aqui; consulte a página do dataset no Kaggle para os termos de uso.
