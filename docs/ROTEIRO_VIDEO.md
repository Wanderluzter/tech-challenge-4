# Roteiro do vídeo (até 5 minutos)

O enunciado permite até 7 minutos; o roteiro fecha em **4:50**. São 11 slides, com a demonstração ao vivo no meio. A apresentação está no claude.ai (Slides), e as falas abaixo também estão nas notas do apresentador de cada slide.

O enunciado pede o *raciocínio técnico*, não um tour pela tela: cada slide responde a um item do PDF (tabela no fim).

## Antes de gravar

- Instale as dependências (`pip install -r requirements.txt`), suba a interface com `uvicorn voc_rag.api:app --port 8000` (com `web/dist` já construído) e abra http://localhost:8000. Zoom do navegador em 125%.
- **A geração leva de 10 a 50 s** com o Gemini gratuito. Não espere ao vivo: abra cada pergunta da demonstração numa aba própria antes de gravar, pelos links abaixo. Na gravação, só troque de aba.
- O piso (0,865) e o limiar de confiança (0,884) vêm de `data/index/manifest.json`. Se o índice foi refeito, rode antes `python -m voc_rag.cli eval --write`; sem isso, o piso volta a 0,80 e não há zona cinzenta.
- Confira o seletor de modelo no cabeçalho: ponto verde = disponível, âmbar = sem cota. Na última avaliação, o `gemini-3.5-flash` estava sem cota e o `gemini-3-flash-preview` respondeu. Cada pergunta respondida gasta 1 chamada da cota; recusas na recuperação não gastam nenhuma.
- Se quiser o painel *Uso do RAG* limpo, apague `data/logs/perguntas.jsonl` antes.

Links da demonstração (cole na barra de endereços):

```text
http://localhost:8000/?q=Quais são os principais problemas relatados pelos clientes?
http://localhost:8000/?q=O que os clientes mais elogiam na categoria beleza e saúde?
http://localhost:8000/?q=Qual é a capital da França?
http://localhost:8000/?q=O que os clientes acham do tempo de bateria do iPhone 15?
```

---

## 1 · Capa — 0:00–0:05

> "Somos Leonardo Botelho e Rafael Silva. Este é o Voz do Cliente."

## 2 · O problema — 0:05–0:25

**Slide:** 38.287 avaliações com comentário; barras da nota média por situação da entrega (3,93 no prazo, 1,88 com atraso, 1,48 sem entrega).

> "A Olist tem 38 mil avaliações com comentário. A nota diz quanto o cliente gostou; o porquê está no texto. Só um exemplo: atraso derruba a nota média em dois pontos. O requisito do sistema é simples: cada afirmação vem das avaliações e, sem evidência, ele não responde, mas diz o que sabe responder."

## 3 · O que o gestor recebe — 0:25–0:40

**Slide:** resposta real para "Quais são os principais problemas relatados pelos clientes?", com citações, e a avaliação [2] em destaque.

> "É isto que o gestor recebe: a resposta organizada por tema, com a contagem aproximada, e cada afirmação com um número que leva à avaliação original. Esta é uma resposta real do sistema."

## 4 · Construção da base de conhecimento — 0:40–0:55

**Slide:** funil 99.224 → 42.687 → 42.370 → 38.287; limpeza, documento e indexação.

> "Das 99 mil avaliações, 57 mil não têm texto: descartamos, porque preencher seria inventar evidência. Sem repetidas e sem textos vazios, ficam 38 mil. Limpamos o texto, cada avaliação vira um documento com os metadados do pedido, e indexamos com embeddings e5 no ChromaDB e no BM25."

## 5 · Arquitetura do pipeline RAG — 0:55–1:20

**Slide:** grafo LangGraph `interpretar → recuperar → gerar → resposta`, com as duas saídas para recusa e a zona cinzenta entre recuperar e gerar.

> "O fluxo pedido no desafio vira um grafo do LangGraph com três nós. Interpretar faz o processamento da pergunta. Recuperar cuida de embeddings, busca e seleção. Gerar monta o contexto e chama o LLM por uma chain LCEL do LangChain. As duas saídas para baixo são o centro do projeto: evidência claramente fraca termina antes do LLM; evidência limítrofe segue para o LLM confirmar se trata do assunto; resposta sem citação válida é descartada."

## 6 · Recuperação e contexto — 1:20–1:50

**Slide:** exemplo real "Quais reclamações relacionadas à entrega aparecem com maior frequência?": 40 + 40 candidatas → 75 após RRF → 44 acima do piso → 12 no contexto.

> "Na prática, para esta pergunta: 'reclamações' vira o filtro nota 1 a 3. A busca vetorial com e5 e o BM25 trazem 40 candidatas cada; a fusão RRF deixa 75; 44 passam do piso de similaridade; o MMR escolhe 12 diferentes entre si. O contexto leva as 12 avaliações numeradas com metadados, mais uma contagem por temas, porque top-k traz exemplos, não frequência."

## 7 · Demonstração — 1:50–3:25

**Tela:** trocar para o navegador. Para cada pergunta: resposta → clicar num número citado → avaliação original → painel "Como chegamos aqui".

- **Pergunta 1 (35 s)** — *Quais são os principais problemas relatados pelos clientes?*
  > "O sistema detecta que é uma pergunta ampla, restringe às notas baixas e a decompõe em sub-buscas pelos temas mais frequentes. Clicando no número, vou direto à avaliação: texto, nota, data, categoria, similaridade e a posição nos rankings vetorial e BM25."
- **Pergunta 2 (20 s)** — *O que os clientes mais elogiam na categoria beleza e saúde?*
  > "Dois filtros inferidos: nota 4 ou 5 e a categoria, aplicados antes da busca. Posso trocá-los no botão Filtros."
- **Pergunta 3 (20 s)** — *Qual é a capital da França?*
  > "Nenhuma avaliação atinge a similaridade mínima: recusa na recuperação, sem chamar o modelo. Mas a recusa não é um beco sem saída: mostra o que a base cobre e sugere perguntas que ela sabe responder; um clique envia a sugestão como nova pergunta."
  >
  > *(Clicar na sugestão chama o LLM e leva de 10 a 50 s. Ou só aponte as sugestões sem clicar, ou clique e corte a espera na edição.)*
- **Pergunta 4 (20 s)** — *O que os clientes acham do tempo de bateria do iPhone 15?*
  > "Parece do domínio, mas só duas avaliações passam do piso, e exigimos três: recusa antes do modelo."

*(Se uma pergunta se comportar diferente na gravação, mostre o que aconteceu e diga por quê. Se nenhum modelo responder, a interface mostra só as evidências: grave essa pergunta de novo.)*

## 8 · Perguntas sem evidência suficiente — 3:25–3:45

**Slide:** um cartão por situação do enunciado, cada um ligado a um nó do grafo.

> "O desafio pede três situações, e cada uma tem uma barreira no grafo. Nada relevante ou fora do escopo: o piso corta antes do LLM. Evidência insuficiente ou limítrofe: o modelo confirma se ela trata do assunto e, se não, recusa. Afirmação sem suporte: a validação descarta respostas sem citação válida."

## 9 · Resultados — 3:45–4:10

**Slide:** 34 quadrados, um por pergunta da avaliação; 30/30 filtros; relevância@k 0,779.

> "Avaliamos com 34 perguntas: 20 com resposta na base e 14 sem, incluindo temas que nem existiam na época dos dados, como Pix. Acertou as 34 decisões entre responder e recusar. Na primeira versão foram 32: as duas falhas eram recusas a mais, em reembolso e atendimento, e as corrigimos com a zona cinzenta e um ajuste no prompt."

## 10 · Desafios e decisões técnicas — 4:10–4:35

**Slide:** faixa de similaridade com a zona cinzenta (piso 0,865, confiança 0,884; fora do escopo até 0,874, no escopo a partir de 0,875); linguagem do gestor × do cliente; frequência.

> "O desafio mais difícil foi calibrar o 'não sei': perguntas válidas e fora do escopo se separavam por só 0,001 de similaridade. Em vez de um corte no fio da navalha, criamos uma zona cinzenta: abaixo do piso, recusa sem custo; na faixa ambígua, o LLM confirma se as avaliações tratam do assunto. Um reranker estreitaria essa faixa. Outro desafio foi a linguagem: o gestor pergunta 'padrões recorrentes', o cliente escreve 'não recebi', então a busca usa só o assunto."

## 11 · Critérios do desafio — 4:35–4:50

**Slide:** os seis critérios esperados do enunciado, cada um com o mecanismo que o atende.

> "Fechando com os critérios do desafio: cada um tem um mecanismo no sistema e um número na avaliação. Código, avaliação e exemplos estão no repositório. Obrigado."

---

## Cobertura do enunciado

| Item exigido no vídeo | Slide |
|---|---|
| Problema de negócio | 2 |
| Arquitetura proposta | 5 |
| Estratégia do pipeline RAG | 4, 5 |
| Como ocorre a recuperação das avaliações | 6 |
| Demonstração prática | 7 |
| Exemplos de perguntas | 3, 7 |
| Evidências recuperadas que fundamentam as respostas | 3, 7 |
| Principais desafios e decisões técnicas | 10 |

Requisitos 1–4 do enunciado: base (slide 4), pipeline (5, 6), evidências (3, 7), perguntas sem evidência (8). Desafio adicional de metadados, com justificativa: slide 6. Critérios esperados: slide 11.

## Dicas de gravação

- Se o grupo dividir a fala: uma pessoa nos slides 1–6, outra na demonstração e nos slides 8–11.
- Grave a demonstração em um take só, sem editar as respostas: respostas reais valem mais que respostas perfeitas.
- Se estourar o tempo, encurte a pergunta 2 da demonstração; as perguntas 1, 3 e 4 são as que mais pontuam nos critérios.
- Não leia o roteiro: use-o como guia de tópicos.
