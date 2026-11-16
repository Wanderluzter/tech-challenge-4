# Roteiro base do vídeo (até 7 minutos)

Alvo: **6min30**, com 30 s de folga. Cerca de 900 palavras faladas no total. O enunciado pede o *raciocínio técnico*, não um tour pela tela — por isso cada bloco da demonstração mostra uma decisão.

**Antes de gravar**
- Streamlit aberto, índice carregado, LLM configurado, zoom do navegador em 125%.
- Rodar as cinco perguntas da demonstração uma vez, para o cache estar quente.
- Abas prontas: (1) README na seção de arquitetura, (2) Streamlit, (3) `eval/resultado.md`.
- Trocar os números entre colchetes `[ ]` pelos da sua execução final.

---

## 0:00 – 0:40 · Problema de negócio

**Tela:** título do projeto; em seguida o funil de dados do README (§4).

> "A Olist tem quase cem mil avaliações de pedidos. A nota diz quanto o cliente ficou satisfeito, mas o porquê está no comentário — e ninguém lê quarenta mil comentários. Nosso projeto transforma esses textos em uma base que um gestor consulta em linguagem natural: quais são os principais problemas, o que os clientes elogiam, o que dizem sobre entrega.
> O requisito mais importante não é escrever bem: é que cada afirmação venha das avaliações, com a evidência visível, e que o sistema diga 'não sei' quando não houver evidência."

## 0:40 – 1:30 · Arquitetura

**Tela:** diagrama Mermaid do README (§2). Acompanhar com o cursor.

> "São dois fluxos. Na ingestão, feita uma vez, juntamos as avaliações aos dados do pedido, limpamos, e cada avaliação vira um documento com metadados. Geramos embeddings com o multilingual-e5-small e indexamos no ChromaDB.
> Na consulta, a pergunta é transformada, passa por uma busca híbrida — vetorial mais BM25 —, os resultados são fundidos, e aqui está o ponto central: antes de chamar o modelo, verificamos se há evidência suficiente. Só então montamos o contexto, o LLM responde citando as avaliações, e validamos as citações."

## 1:30 – 2:20 · Base de conhecimento

**Tela:** tabela do funil (README §4) e, rapidamente, `data_prep.py`.

> "Das 99 mil avaliações, 57 mil não têm texto. Descartamos: não há o que recuperar, e preencher texto ausente seria fabricar evidência. Removemos avaliações duplicadas e comentários sem conteúdo, como 'ok' e 'bom'. Ficaram 38 mil documentos.
> Não fizemos chunking: a mediana é de 59 caracteres, então uma avaliação é uma unidade de evidência, rastreável pelo ID.
> E enriquecemos com metadados: nota, data, categoria e — o mais útil — a situação real da entrega, calculada pelas datas do pedido, não pelo que o cliente escreveu."

## 2:20 – 4:50 · Demonstração (o coração do vídeo)

**Tela:** Streamlit. Para cada pergunta: resposta → evidências → painel "Como chegamos aqui".

**Pergunta 1 — ampla (≈ 45 s):** *Quais são os principais problemas relatados pelos clientes?*

> "Essa pergunta não tem um assunto para buscar: a palavra 'problemas' só acharia quem escreveu 'problemas'. O sistema detecta que é uma pergunta ampla, restringe às notas baixas e a decompõe em sub-buscas pelos temas mais frequentes desse recorte — vejam aqui no painel. A resposta vem organizada por tema, e cada tópico cita as avaliações. Clicando, vejo o texto original, a nota, a data e a similaridade."

**Pergunta 2 — tema específico (≈ 35 s):** *O que os clientes relatam sobre problemas relacionados à entrega?*

> "Aqui o texto de busca vira 'problemas entrega': removemos o vocabulário analítico, que não existe nas avaliações. Reparem nos dois rankings: algumas evidências vieram da busca vetorial, outras do BM25. A fusão é por Reciprocal Rank Fusion, e o MMR evita doze cópias de 'não recebi o produto'."

**Pergunta 3 — metadados (≈ 35 s):** *O que os clientes mais elogiam na categoria beleza e saúde?*

> "O sistema inferiu dois filtros sozinho: nota 4 ou 5 e a categoria. Eles são aplicados no banco vetorial antes da busca. Posso sobrescrever manualmente na lateral — por exemplo, só pedidos entregues com atraso."

**Pergunta 4 — fora do escopo (≈ 20 s):** *Qual é a capital da França?*

> "Nenhuma avaliação atinge a similaridade mínima. O sistema recusa na etapa de recuperação — o modelo de linguagem nem é chamado, então não há o que alucinar."

**Pergunta 5 — do domínio, mas sem resposta (≈ 25 s):** *O que os clientes acham do tempo de bateria do iPhone 15?*

> "Esse caso é mais traiçoeiro: a busca encontra avaliações sobre celulares e baterias, então passa pela primeira barreira. Quem recusa é o modelo, instruído a não responder quando as evidências não tratam do que foi perguntado. As evidências continuam visíveis para auditoria."

*(Se a pergunta 5 não se comportar assim com o seu modelo, mostre o que aconteceu e diga por quê. É um ótimo gancho para o bloco de desafios.)*

## 4:50 – 5:40 · Como garantimos respostas fundamentadas

**Tela:** expander "Contexto enviado ao modelo" e, depois, a tabela das três barreiras (README §6).

> "Este é o contexto exato que o modelo recebe: as avaliações numeradas com metadados e um panorama quantitativo do recorte. O panorama existe porque busca top-k traz exemplos, não contagens — sem ele, 'com maior frequência' seria um chute a partir de doze avaliações.
> São três barreiras: o limiar de similaridade na recuperação; a instrução de recusa na geração; e uma validação depois da geração, que remove citações inexistentes e descarta respostas sem nenhuma citação."

## 5:40 – 6:30 · Desafios, decisões e resultados

**Tela:** `eval/resultado.md` e a tabela de decisões (README §10).

> "Três desafios. Primeiro, o descompasso entre a linguagem do gestor e a do cliente, resolvido com o foco no assunto e a expansão por temas — a relevância das evidências subiu de [0,61] para [0,74] no nosso conjunto de avaliação.
> Segundo, calibrar o 'não sei': montamos [25] perguntas, dentro e fora do escopo, e um script que escolhe o limiar. O resultado foi [X de 25] decisões corretas entre responder e recusar.
> Terceiro, frequência: resolvemos com temas por palavras-chave — uma aproximação transparente, apresentada como aproximada.
> Como próximos passos: um reranker e um verificador de fidelidade das citações. O código, o README e os exemplos estão no repositório. Obrigado!"

---

## Distribuição do tempo

| Bloco | Duração | Item exigido no enunciado |
|---|---|---|
| Problema | 0:40 | Problema de negócio |
| Arquitetura | 0:50 | Arquitetura proposta |
| Base de conhecimento | 0:50 | Estratégia do pipeline RAG |
| Demonstração | 2:30 | Demonstração prática · exemplos de perguntas · evidências recuperadas · como ocorre a recuperação |
| Fundamentação | 0:50 | Evidências que fundamentam as respostas |
| Desafios e decisões | 0:50 | Principais desafios e decisões técnicas |
| **Total** | **6:30** | |

## Dicas de gravação

- Se o grupo tiver mais de uma pessoa, divida por bloco (uma apresenta contexto e arquitetura, outra a demonstração, outra as decisões).
- Grave a demonstração em um take só, sem editar as respostas: respostas reais valem mais que respostas perfeitas.
- Se estourar o tempo, corte primeiro a pergunta 2; as perguntas 1, 4 e 5 são as que mais pontuam nos critérios.
- Não leia o roteiro: use-o como guia de tópicos.
