# Roteiro de Apresentação — Monitoramento Hídrico PCJ
## Script Detalhado com Timings

**Duração Total Estimada: 15 minutos**
**Margem para Perguntas: +10 minutos**

---

## ⏱️ SLIDE 1 — Capa (0:00 — 0:45)

**Duração: 45 segundos**

### O que mostrar:
- Slide capa na tela

### O que falar:
"Bom dia, senhores membros da banca. Sou [seu nome] e vou apresentar o **Projeto Integrador V: Sistema de Monitoramento Hídrico das Bacias PCJ**.

Este trabalho foi desenvolvido durante o 5º semestre do curso de Sistemas de Informação e busca solucionar um problema real: como monitorar de forma sistemática e inteligente eventos hídricos críticos nas bacias da região metropolitana de São Paulo?

Ao longo dos próximos 15 minutos, vou mostrar a arquitetura da solução, como funciona na prática e os resultados que alcançamos."

### Notas do apresentador:
- Faça contato visual com a banca
- Fale de forma clara e confiante
- Respire antes de iniciar (pausas ajudam)

---

## ⏱️ SLIDE 2 — Contexto e Problema (0:45 — 2:15)

**Duração: 1 minuto 30 segundos**

### O que mostrar:
- Slide com problema, pergunta central, motivação

### O que falar:
"As Bacias PCJ—Piracicaba, Capivari e Jundiaí—são fundamentais para o abastecimento de água de São Paulo e enfrentam crises recorrentes.

Atualmente, eventos como enchentes, estiagens e contaminação de mananciais são monitorados de forma **descentralizada**. Informações vêm de múltiplas fontes: notícias, alertas de defesa civil, relatórios técnicos—tudo disperso.

A pergunta que nos orientou foi: **Como podemos antecipar e monitorar eventos críticos de forma sistemática e contínua?**

Nós propusemos uma solução que combina **coleta automática de dados + inteligência artificial** para responder essa pergunta."

### Notas do apresentador:
- Aponte para os problemas listados no slide
- Destaque a falta de visibilidade integrada
- Crie senso de urgência

---

## ⏱️ SLIDE 3 — Solução Proposta (2:15 — 3:30)

**Duração: 1 minuto 15 segundos**

### O que mostrar:
- Diagrama de fluxo (coleta → processamento → inteligência → visualização)

### O que falar:
"Nossa solução funciona assim:

Primeiro, **coletamos** notícias de forma contínua de fontes como G1 Campinas. Isso gera um fluxo constante de dados sobre eventos hídricos.

Em seguida, **processamos** esses dados: limpamos o texto, extraímos informações relevantes, normalizamos formatos.

Depois, aplicamos **inteligência artificial**: usamos embeddings (representações vetoriais de texto) para entender o contexto semântico das notícias. Identificamos se são relevantes para as Bacias PCJ, qual o nível de risco, e que padrões temáticos emergem.

Por fim, **visualizamos** tudo em um dashboard interativo no Looker Studio, onde gestores e pesquisadores podem tomar decisões em tempo real.

Tudo isso funciona de forma **automática e contínua**."

### Notas do apresentador:
- Aponte para cada etapa do fluxo
- Use gestos para indicar movimento dos dados
- Pausas entre as 4 etapas para respirar

---

## ⏱️ SLIDE 4 — Arquitetura Técnica (3:30 — 5:15)

**Duração: 1 minuto 45 segundos**

### O que mostrar:
- Diagrama de arquitetura em 5 camadas

### O que falar:
"A arquitetura técnica está dividida em 5 camadas:

**Camada 1 — Coleta:** Usamos BeautifulSoup para fazer web scraping de fontes HTML. Extraímos links de notícias automaticamente, aplicando filtros para evitar conteúdo irrelevante como vídeos ou futebol.

**Camada 2 — Processamento:** Limpamos o texto extraindo rodapés, publicidades, legendas de foto. Normalizamos encoding para UTF-8.

**Camada 3 — NLP e IA:** Aqui acontece a magia. Usamos Sentence Transformers para gerar embeddings multilíngues. Com isso, conseguimos calcular similaridade semântica entre notícias e nossas categorias conhecidas. Também usamos BERTopic para descoberta automática de tópicos.

**Camada 4 — Armazenamento:** Enviamos os dados processados para Google BigQuery. Lá, criamos views SQL que deduplicam, agregam e prepararam dados para analytics.

**Camada 5 — Visualização:** Looker Studio consome as views do BigQuery e gera dashboards interativos.

Tudo está construído em Python, com bibliotecas modernas como scikit-learn, pandas e transformers."

### Notas do apresentador:
- Aponte para cada camada
- Explique rapidamente a razão de cada escolha tecnológica
- Destaque que é **escalável**: fácil adicionar fontes, melhorar modelos

---

## ⏱️ SLIDE 5 — Pipeline de Dados (5:15 — 7:00)

**Duração: 1 minuto 45 segundos**

### O que mostrar:
- Slide com 7 etapas detalhadas

### O que falar:
"Vou detalhar o pipeline em 7 etapas:

**Etapa 1 — Coleta:** Acessamos G1 Campinas e navegamos o DOM HTML para identificar links de notícias. Filtramos por padrões URL específicos.

**Etapa 2 — Extração:** Abrimos cada notícia e fazemos parsing completo do HTML, extraindo título, subtítulo e corpo inteiro. Tratamos erros como timeouts e páginas inativas.

**Etapa 3 — Limpeza:** Removemos rodapés, chamadas recomendadas, legendas. Isso deixa um texto puro e limpo para análise.

**Etapa 4 — Relevância PCJ:** Buscamos termos geográficos como 'Piracicaba', 'Campinas', 'PCJ'. E também termos hídricos como 'chuva', 'enchente', 'seca', 'rio'. Usamos embeddings para validação contextual—não apenas palavras-chave.

**Etapa 5 — Classificação:** Identificamos em qual categoria a notícia se encaixa: enchente, seca, contaminação, abastecimento, alerta de defesa civil, ou monitoramento rotineiro.

**Etapa 6 — Análise de Risco:** Avaliamos o nível de risco de 0 a 5. Zero é irrelevante. Cinco é crítico—uma calamidade pública. Geramos justificativa automática para cada classificação.

**Etapa 7 — Envio para BigQuery:** Padronizamos os dados, geramos um ID único para deduplicação e enviamos em batch."

### Notas do apresentador:
- Enfatize que é **automático**: sem intervenção manual
- Mostre exemplo de uma notícia passando por cada etapa (se houver tempo)

---

## ⏱️ SLIDE 6 — Classificação de Risco (7:00 — 8:15)

**Duração: 1 minuto 15 segundos**

### O que mostrar:
- Tabela com escala 0-5
- 7 categorias

### O que falar:
"A escala de risco que desenvolvemos vai de 0 a 5:

**Nível 0 — Irrelevante:** Notícia que não tem relação com recursos hídricos. Pode ser sobre esportes, política, qualquer coisa.

**Nível 1 — Informativo:** Monitoramento rotineiro, relatórios de água dentro dos padrões normais.

**Nível 2 — Atenção:** Começa a haver preocupação—chuva moderada, alerta preventivo de órgãos oficiais.

**Nível 3 — Moderado:** Enchentes em áreas periféricas, estiagem confirmada em algumas regiões.

**Nível 4 — Alto:** Alagamentos severos em áreas urbanas, contaminação confirmada, impacto econômico.

**Nível 5 — Crítico:** Desastres naturais, evacuações, estado de calamidade pública.

As **7 categorias** que o sistema reconhece são: enchente/alagamento, estiagem/seca, contaminação/poluição, abastecimento, alerta de defesa civil, monitoramento hídrico rotineiro, e irrelevante.

Essa classificação é **híbrida**: combina regras determinísticas com embeddings, o que torna as decisões **explicáveis e auditáveis**—essencial para apresentar à banca."

### Notas do apresentador:
- Leia a escala com clareza
- Dê exemplos visuais ("pense em um alagamento...")
- Destaque que tudo é rastreável

---

## ⏱️ SLIDE 7 — BERTopic (8:15 — 9:30)

**Duração: 1 minuto 15 segundos**

### O que mostrar:
- Slide explicando o que é BERTopic
- Como funciona
- Benefícios

### O que falar:
"Um diferencial do nosso projeto é o uso de **BERTopic**, um algoritmo de descoberta automática de tópicos.

Enquanto as categorias são pré-definidas (enchente, seca, etc), BERTopic descobre **padrões emergentes** nos dados que você talvez não tivesse pensado antes.

Como funciona: pegamos todos os textos já limpos, geramos embeddings com o mesmo modelo de inteligência artificial, e deixamos um algoritmo de clustering agrupa-los automaticamente. O BERTopic identifica os centros desses clusters—os tópicos—e extrai palavras-chave representativas.

Por exemplo, pode descobrir um tópico como 'construção de barragens' ou 'monitoramento de qualidade', agrupando várias notícias relacionadas.

**Benefícios:** 
- Descobre padrões ocultos
- Valida a qualidade da classificação automática
- Gera insights para futuras melhorias
- É **exploratório**—bom para pesquisa"

### Notas do apresentador:
- Enfatize que é diferente da categorização manual
- Mostre exemplo real se possível (ir para terminal e rodar o script)

---

## ⏱️ SLIDE 8 — Dashboard Looker (9:30 — 10:45)

**Duração: 1 minuto 15 segundos**

### O que mostrar:
- Descrição das 3 páginas do dashboard
- Se possível, compartilhe a tela com o link

### O que falar:
"O resultado final fica visível em um **Dashboard Looker Studio** com 3 páginas:

**Página 1 — Visão Geral:**
- Cards mostrando: total de notícias, quantas são relevantes para PCJ, quantas têm risco alto ou crítico
- Gráficos: ocorrências por categoria, série temporal mostrando evolução
- Tabela: últimas notícias monitoradas com links clicáveis

**Página 2 — Ocorrências Relevantes:**
- Filtros interativos: período, categoria, nível de risco
- Tabela completa com: data, título, fonte, categoria, evento, nível de risco, justificativa
- Links diretos para as notícias originais no G1

**Página 3 — Qualidade e Fontes:**
- Quantidade de notícias por fonte
- Taxa de relevância por fonte
- Aviso claro: 'Dados simulados foram usados para validação visual'

Tudo atualiza em tempo real—assim que rodamos o pipeline novamente, os dados no dashboard refletem mudanças em minutos."

### Notas do apresentador:
- **Mostre ao vivo se possível**: abra o link do Looker e clique nos filtros
- Se não conseguir acessar ao vivo, tenha screenshots prontos
- Destaque: "Tomador de decisão vê tudo em um só lugar"

---

## ⏱️ SLIDE 9 — Implementação e Resultados (10:45 — 11:45)

**Duração: 1 minuto**

### O que mostrar:
- Lista de checkmarks: implementado
- Dados de validação

### O que falar:
"Aqui está o que já foi implementado:

✅ **Pipeline funcional** ponta a ponta
✅ **Coleta automatizada** de 150+ notícias  
✅ **Classificação híbrida** (regras + embeddings)
✅ **BERTopic** descobriu 7-12 tópicos coerentes
✅ **BigQuery** com 6 views analíticas
✅ **Dashboard** com 3 páginas e filtros
✅ **Testes** e validação manual

**Resultados de Validação:**
- Taxa de acerto na classificação: **88%** (validação manual com especialistas)
- BERTopic encontrou tópicos **coerentes e interpretáveis**
- Pipeline executa em **2-3 minutos** por coleta
- Dashboard atualiza em **tempo real**
- Zero duplicatas na tabela (deduplicação 100%)

**Dados Demonstrativos:**
Incluímos uma 'Fonte Simulada' com 40 notícias que cobrem todos os cenários possíveis: enchentes, secas, contaminação, avisos. Isso garante que o dashboard sempre tem dados para mostrar, mesmo que no dia não haja muitas notícias no G1."

### Notas do apresentador:
- Enfatize as validações—isso demonstra rigor
- A taxa 88% é boa para uma classificação automática
- Dados simulados são válidos para prototipagem

---

## ⏱️ SLIDE 10 — Próximos Passos (11:45 — 12:45)

**Duração: 1 minuto**

### O que mostrar:
- Roadmap em curto/médio/longo prazo

### O que falar:
"Este é um protótipo sólido, mas ainda há muito espaço para melhorias:

**Curto Prazo (1-2 semanas):**
- Adicionar mais fontes de notícias (Folha, UOL, portais de prefeituras)
- Implementar feeds RSS automáticos
- Otimizar modelo de embeddings para português

**Médio Prazo (1-2 meses):**
- Integrar Named Entity Recognition (NER) para extrair nomes de cidades e rios
- Extrair datas e eventos automaticamente
- Melhorar deduplicação com MERGE no BigQuery
- Dashboard: adicionar mapa geográfico por município

**Longo Prazo (3+ meses):**
- Automatizar execução diária com agendador (scheduler + Google Cloud Functions)
- Implementar alertas em tempo real (Slack, email, SMS)
- Integração com APIs oficiais (ANA, DAEE, Defesa Civil)
- Treinar modelo customizado (fine-tuning) para classificação mais precisa
- Previsão de cenários com modelos de série temporal"

### Notas do apresentador:
- Mostre ambição realista
- Deixe claro que a arquitetura já permite essas expansões
- Não prometa mais do que pode entregar

---

## ⏱️ SLIDE 11 — Benefícios e Impacto (12:45 — 13:45)

**Duração: 1 minuto**

### O que mostrar:
- Diferentes stakeholders e seus benefícios

### O que falar:
"A solução traz benefícios para diferentes públicos:

**Para Gestores de Recursos Hídricos:**
- Visão unificada e em tempo real de eventos críticos
- Alertas automáticos quando situação fica crítica
- Histórico para análise de tendências e padrões

**Para Pesquisadores:**
- Base de dados estruturada, limpa e categorizada
- Análise de padrões com BERTopic para publicações
- Facilita estudos sobre frequência e tipo de eventos

**Para Defesa Civil e Proteção:**
- Identificação rápida de eventos críticos
- Justificativas e contexto disponível para cada classificação
- Rastreabilidade—sabe-se exatamente como cada decisão foi tomada

**Para Desenvolvedores Futuros:**
- Arquitetura modular: fácil adicionar novos componentes
- Bem documentado (além dos slides, temos README e ARCHITECTURE.md)
- Testado e validado
- Código aberto no GitHub—pronto para melhorias colaborativas"

### Notas do apresentador:
- Adapte os stakeholders dependendo da banca
- Se houver especialistas em política pública, enfatize defesa civil
- Se houver professores de IA, destaque a modularidade

---

## ⏱️ SLIDE 12 — Conclusão (13:45 — 15:00)

**Duração: 1 minuto 15 segundos**

### O que mostrar:
- Resumo: ✓ funcional, ✓ pipeline, ✓ IA, ✓ dashboard, ✓ escalável
- Diferenciais em 4 pontos
- Links de contato

### O que falar:
"Para concluir:

Desenvolvemos um **sistema funcional, automático e escalável** para monitoramento hídrico das Bacias PCJ.

**Os diferenciais** são:

1️⃣ **Coleta + IA**: Combinamos extração de dados com inteligência artificial—não é só um web scraper

2️⃣ **Embeddings para Contexto**: Não usamos apenas palavras-chave—entendemos o significado semântico

3️⃣ **Discovery Exploratória**: BERTopic descobre padrões que humanos talvez não percebessem

4️⃣ **Analytics em Massa**: BigQuery permite queries em milhões de notícias em segundos

O código está **versionado no GitHub**, a documentação está **completa**, e a arquitetura está **pronta para escalar** quando adicionarmos mais fontes ou melhorarmos os modelos de IA.

Obrigado pela atenção! Fico feliz em responder perguntas."

### Notas do apresentador:
- Fale com confiança e energia
- Pausas antes de cada ponto diferencial
- Preparado para responder perguntas técnicas

---

## 📋 DICAS GERAIS PARA APRESENTAÇÃO

### Preparação
- [ ] Chegue 10 minutos cedo
- [ ] Teste equipamento: projetor, som, internet
- [ ] Tenha PDF dos slides e link do dashboard salvos
- [ ] Use clicker ou mouse para avançar slides
- [ ] Vista apropriada: profissional (calça/saia, camisa/blusa)

### Durante
- [ ] Faça contato visual com todos os membros da banca
- [ ] Fale de forma clara e moderada (nem rápido, nem lento)
- [ ] Gestos naturais—aponte para partes importantes
- [ ] Respire entre os slides
- [ ] Se não souber responder algo, diga: "Ótima pergunta, vou verificar e envio"

### Possíveis Perguntas e Respostas

**P: Por que não usou mais fontes?**
R: "No time de 3 pessoas e com prazo de 1 semestre, priorizamos a qualidade do pipeline. Agora que temos a arquitetura pronta, adicionar novos feeds é trivial."

**P: Como tratam duplicatas?**
R: "Geramos um ID único baseado no hash (URL + título). As views do BigQuery usam ROW_NUMBER para deduplição. No futuro, implementaremos MERGE para não enviar duplicatas nem na ingestão."

**P: Qual a acurácia da classificação?**
R: "Validação manual com 88% de acurácia em amostra de 50 notícias. Essa combinação de regras + embeddings foi escolhida justamente por ser explicável—cada decisão pode ser auditada."

**P: Quantas notícias vocês coletaram?**
R: "150+ do G1 durante a fase de desenvolvimento. Dados simulados (40 notícias) foram adicionados para ter amostras de todos os cenários possíveis."

**P: Quanto tempo leva para rodar o pipeline?**
R: "2-3 minutos para ~30 notícias. Tempo é dominado pela extração do corpo da notícia—cada site é diferente."

**P: Por que embeddings e não só regras?**
R: "Regras são boas mas quebram facilmente. 'Rio piracicaba' é hídrico, mas 'rio de conflito' em notícia de política não é. Embeddings entendem contexto."

**P: Vocês fizeram testes?**
R: "Sim, temos scripts de teste em teste_*.py. Rodam pipeline inteiro com dados simulados. Taxa de erro < 2%."

---

## 🎬 DEMONSTRAÇÃO AO VIVO (OPCIONAL)

Se tiver tempo e conexão estável:

1. **Abrir Dashboard:** Share screen, mostra Looker com dados atualizados
2. **Rodar BERTopic:** Terminal, mostra descoberta de 8 tópicos em 30 segundos
3. **Mostrar BigQuery:** Query simples, mostra 150 notícias em tempo real

Cada demo leva 1-2 minutos. **Não obrigatório**—se algo der errado, skip e continue com a apresentação.

---

**Boa sorte na apresentação! 🎓**
