# Roteiro base do vídeo (até 7 minutos)

Alvo: **6min30**, com 30 s de folga. Cerca de 900 palavras faladas no total. O enunciado pede o *raciocínio técnico*, não um tour pela tela — por isso cada bloco da demonstração mostra uma decisão.

**Antes de gravar**
- Suba a interface: `uvicorn voc_rag.api:app --port 8000` (com `web/dist` já construído) e abra http://localhost:8000. Zoom do navegador em 125%.
- **A geração leva de 10 a 40 s** com o LLM gratuito. Não espere ao vivo: abra cada pergunta da demonstração numa aba própria antes de gravar, usando o link direto `http://localhost:8000/?q=<pergunta>` (exemplos abaixo). Na gravação, só troque de aba.
- Cada pergunta feita gasta 1 chamada da cota do LLM (recusas na recuperação, nenhuma). Ensaiar a demo inteira gasta cerca de 5.
- Abas prontas, na ordem: (1) README na seção de arquitetura, (2) a tabela do funil (README §4), (3–7) as cinco perguntas, (8) Dashboard › Base de avaliações, (9) Dashboard › Qualidade.
- Se quiser o painel *Uso do RAG* limpo, apague `data/logs/perguntas.jsonl` antes de abrir as abas.

Links das perguntas (cole na barra de endereços):

```text
http://localhost:8000/?q=Quais são os principais problemas relatados pelos clientes?
http://localhost:8000/?q=O que os clientes relatam sobre problemas relacionados à entrega?
http://localhost:8000/?q=O que os clientes mais elogiam na categoria beleza e saúde?
http://localhost:8000/?q=Qual é a capital da França?
http://localhost:8000/?q=O que os clientes acham do tempo de bateria do iPhone 15?
```

---

## 0:00 – 0:40 · Problema de negócio

**Tela:** título do projeto; em seguida o Dashboard › Base de avaliações (cards do topo e o gráfico "Entrega é o que mais derruba a nota").

> "A Olist tem quase cem mil avaliações de pedidos. A nota diz quanto o cliente ficou satisfeito, mas o porquê está no comentário — e ninguém lê quarenta mil comentários. Só aqui: pedidos atrasados têm nota média dois pontos menor que os entregues no prazo. Nosso projeto transforma esses textos em uma base que um gestor consulta em linguagem natural.
> O requisito mais importante não é escrever bem: é que cada afirmação venha das avaliações, com a evidência visível, e que o sistema diga 'não sei' quando não houver evidência."

## 0:40 – 1:30 · Arquitetura

**Tela:** diagrama Mermaid do README (§2). Acompanhar com o cursor.

> "São dois fluxos. Na ingestão, feita uma vez, juntamos as avaliações aos dados do pedido, limpamos, e cada avaliação vira um documento com metadados. Geramos embeddings com o multilingual-e5-small e indexamos no ChromaDB.
> Na consulta, a pergunta é transformada, passa por uma busca híbrida — vetorial mais BM25 —, os resultados são fundidos, e aqui está o ponto central: antes de chamar o modelo, verificamos se há evidência suficiente. Só então montamos o contexto, o LLM responde citando as avaliações, e validamos as citações. Uma API em FastAPI expõe esse pipeline para a interface em React."

## 1:30 – 2:20 · Base de conhecimento

**Tela:** tabela do funil (README §4) e, rapidamente, `data_prep.py`.

> "Das 99 mil avaliações, 57 mil não têm texto. Descartamos: não há o que recuperar, e preencher texto ausente seria fabricar evidência. Removemos avaliações duplicadas e comentários sem conteúdo, como 'ok' e 'bom'. Ficaram 38 mil documentos.
> Não fizemos chunking: a mediana é de 59 caracteres, então uma avaliação é uma unidade de evidência, rastreável pelo ID.
> E enriquecemos com metadados: nota, data, categoria, estado e — o mais útil — a situação real da entrega, calculada pelas datas do pedido, não pelo que o cliente escreveu."

## 2:20 – 4:50 · Demonstração (o coração do vídeo)

**Tela:** página Perguntar. Para cada pergunta: resposta → clicar num número citado → evidência destacada → painel "Como chegamos aqui" à direita.

**Pergunta 1 — ampla (≈ 45 s):** *Quais são os principais problemas relatados pelos clientes?*

> "Essa pergunta não tem um assunto para buscar: a palavra 'problemas' só acharia quem escreveu 'problemas'. O sistema detecta que é uma pergunta ampla, restringe às notas baixas e a decompõe em sub-buscas pelos temas mais frequentes desse recorte — vejam aqui no painel. A resposta vem organizada por tema, e cada tópico cita as avaliações. Clicando no número, vou direto à avaliação: texto original, nota, data, categoria e similaridade."

**Pergunta 2 — tema específico (≈ 35 s):** *O que os clientes relatam sobre problemas relacionados à entrega?*

> "Aqui o texto de busca vira 'problemas entrega': removemos o vocabulário analítico, que não existe nas avaliações. Reparem nos dois rankings em cada evidência: algumas vieram da busca vetorial, outras do BM25. A fusão é por Reciprocal Rank Fusion — o funil ao lado mostra quantas candidatas cada busca trouxe e quantas passaram do limiar —, e o MMR evita doze cópias de 'não recebi o produto'."

**Pergunta 3 — metadados (≈ 35 s):** *O que os clientes mais elogiam na categoria beleza e saúde?*

> "O sistema inferiu dois filtros sozinho: nota 4 ou 5 e a categoria. Eles são aplicados no banco vetorial antes da busca. Posso sobrescrever manualmente no botão Filtros — por exemplo, só pedidos entregues com atraso, ou só um estado."

**Pergunta 4 — fora do escopo (≈ 20 s):** *Qual é a capital da França?*

> "Nenhuma avaliação atinge a similaridade mínima. O sistema recusa na etapa de recuperação — o modelo de linguagem nem é chamado, então não há o que alucinar, e não há custo."

**Pergunta 5 — do domínio, mas sem resposta (≈ 25 s):** *O que os clientes acham do tempo de bateria do iPhone 15?*

> "Esse caso parece do domínio — fala de clientes e de um produto —, mas a base é de 2016 a 2018 e não tem nada sobre isso. Apenas uma avaliação atinge a similaridade mínima, e exigimos pelo menos três: o sistema recusa antes de chamar o modelo. Quando a busca encontra avaliações parecidas mas que não respondem — como 'qual foi o faturamento em 2018' —, quem recusa é o próprio LLM, instruído a não responder sem evidência."

*(Se a pergunta 5 se comportar diferente na gravação, mostre o que aconteceu e diga por quê. É um ótimo gancho para o bloco de desafios.)*

## 4:50 – 5:40 · Como garantimos respostas fundamentadas

**Tela:** no painel "Como chegamos aqui", abrir "Contexto enviado ao modelo"; depois, a tabela das três barreiras (README §6).

> "Este é o contexto exato que o modelo recebe: as avaliações numeradas com metadados e um panorama quantitativo do recorte. O panorama existe porque busca top-k traz exemplos, não contagens — sem ele, 'com maior frequência' seria um chute a partir de doze avaliações.
> São três barreiras: o limiar de similaridade na recuperação; a instrução de recusa na geração; e uma validação depois da geração, que remove citações inexistentes e descarta respostas sem nenhuma citação."

## 5:40 – 6:30 · Desafios, decisões e resultados

**Tela:** Dashboard › Qualidade (cards do topo e o gráfico "Onde o limiar separa o que responder do que recusar").

> "Para medir, montamos 34 perguntas: as do enunciado, seis nossas, dez fora do escopo e quatro do domínio sem resposta na base — como pagamento com Pix, que nem existia na época dos dados. O sistema acertou 32 de 34 decisões entre responder e recusar, e recusou corretamente as 14 que não tinham resposta. Os dois erros foram recusas a mais, nunca respostas inventadas: o sistema erra para o lado seguro.
> O principal desafio foi calibrar o 'não sei'. Este gráfico mostra cada pergunta pela similaridade da terceira melhor evidência: o limiar de 0,875 separa os dois grupos, mas com uma margem de apenas 0,001 — o embedding comprime as similaridades. É a nossa principal limitação, e um reranker é o próximo passo.
> Outro desafio foi a linguagem: o gestor pergunta 'quais padrões recorrentes', o cliente escreve 'não recebi'. Resolvemos tirando o vocabulário analítico da busca e expandindo perguntas amplas pelos temas mais frequentes. E para 'com maior frequência', o modelo recebe uma contagem por temas, apresentada como aproximada.
> O código, o README e os exemplos estão no repositório. Obrigado!"

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
- Confira o seletor de modelo no cabeçalho antes de gravar: ponto verde = disponível, âmbar = sem cota. Se o modelo cair durante a gravação, a resposta vem de outro modelo com um aviso amarelo (dá para mencionar como recurso de resiliência); se nenhum responder, a interface mostra só as evidências — grave essa pergunta de novo.
- Não leia o roteiro: use-o como guia de tópicos.
