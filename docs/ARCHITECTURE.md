# ARCHITECTURE.md — Documentação Técnica Completa

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura de Camadas](#arquitetura-de-camadas)
3. [Pipeline de Dados](#pipeline-de-dados)
4. [Módulos Python](#módulos-python)
5. [Modelos de IA](#modelos-de-ia)
6. [BigQuery e Views](#bigquery-e-views)
7. [Como Estender](#como-estender)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O **Monitoramento Hídrico das Bacias PCJ** é um sistema de ponta a ponta que:

1. Coleta notícias de múltiplas fontes
2. Processa texto com NLP
3. Classifica usando IA (embeddings + BERTopic)
4. Armazena em BigQuery
5. Visualiza em dashboard Looker Studio

**Tecnologias:**
- Python 3.12
- BeautifulSoup4 (web scraping)
- Pandas (data processing)
- Sentence-Transformers (embeddings)
- BERTopic (topic discovery)
- Google BigQuery (data warehouse)
- Looker Studio (BI)

---

## Arquitetura de Camadas

### Camada 1: Coleta
**Responsáveis:** `src/collectors/`

```
BeautifulSoup4 + Requests
         ↓
    BS4Collector
         ↓
   NewsExtractor
         ↓
   Lista de URLs
```

**Fluxo:**
```python
# 1. Coletor identifica links
coletor = BS4Collector(
    nome_fonte="G1 Campinas e Regiao",
    url_base="https://g1.globo.com/sp/campinas-regiao/"
)
noticias = coletor.coletar()  # → [{"url": "...", "titulo": "..."}, ...]

# 2. Extrator pega corpo de cada notícia
extrator = NewsExtractor()
dados = extrator.extrair("https://...")  
# → {"titulo_extraido": "...", "texto_original": "...", "erro_extracao": None}
```

**Arquivos:**
- `src/collectors/base_collector.py` — classe abstrata
- `src/collectors/bs4_collector.py` — implementação HTML
- `src/collectors/news_extractor.py` — parsing de corpo

**Configuração de fontes:**
- `src/config/fontes.yaml` — lista de URLs a monitorar

---

### Camada 2: Processamento
**Responsáveis:** `src/processing/`

```
Texto bruto
    ↓
Cleaner (limpeza)
    ↓
Relevance Filter (relevância PCJ)
    ↓
Occurrence Formatter (padronização)
    ↓
Texto limpo + metadados
```

**Componentes:**

1. **cleaner.py** — Remove ruído
   ```python
   texto_limpo = limpar_texto_noticia(texto_original)
   # Remove: rodapés, legendas, links, espaços extras
   ```

2. **relevance_filter.py** — Filtra por PCJ
   ```python
   resultado = explicar_relevancia_pcj(titulo, texto_limpo)
   # → {"relevante": True, "termos_pcj": [...], "confianca": 0.95}
   ```

3. **occurrence_formatter.py** — Padroniza
   ```python
   ocorrencia_padrao = padronizar_ocorrencia(noticia)
   # Adiciona: id único, timestamps, campos faltantes
   ```

---

### Camada 3: NLP e IA
**Responsáveis:** `src/nlp/`

```
Texto limpo
    ↓
Embedding (Sentence-Transformers)
    ↓
┌─────────────────────┬──────────────────┐
│ Risk Classifier     │  BERTopic        │
│ (categorização)     │ (descoberta)      │
└─────────────────────┴──────────────────┘
    ↓                      ↓
Categoria + Risco     Tópicos descobertos
```

**1. Embeddings (Modelos de Linguagem)**

Modelo: `paraphrase-multilingual-MiniLM-L12-v2`

Características:
- 384 dimensões
- 50+ idiomas suportados
- Rápido (~50ms por texto)
- Treina em CPU

Uso:
```python
from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
embedding = modelo.encode("Rio Piracicaba cheio")  # → array [0.1, 0.2, ...]
```

**2. Risk Classifier**

Arquivo: `src/nlp/risk_classifier.py`

Fluxo:
```
Texto limpo + relevante_pcj
    ↓
Calcula similaridade com categorias conhecidas
    ↓
Seleciona categoria com maior similaridade
    ↓
Mapeia para nível de risco (0-5)
    ↓
Gera justificativa automática
```

Categorias:
```python
CATEGORIAS = {
    "enchente_alagamento": "Eventos de água em excesso",
    "estiagem_seca": "Escassez ou seca",
    "contaminacao_poluicao": "Qualidade comprometida",
    "abastecimento": "Sistemas de distribuição",
    "alerta_defesa_civil": "Avisos oficiais",
    "monitoramento_hidrico": "Estudos e relatórios",
    "irrelevante": "Sem relação hídrica"
}
```

Escala de risco:
```
0: Irrelevante (não trata de hidrologia)
1: Informativo (monitoramento rotineiro)
2: Atenção (começa haver preocupação)
3: Moderado (impacto localizado)
4: Alto (impacto severo)
5: Crítico (desastre, calamidade pública)
```

**3. BERTopic**

Arquivo: `src/nlp/bertopic_analyzer.py`

Algoritmo:
```
Textos
  ↓
Gera embeddings de todos
  ↓
Agrupa por similaridade (HDBSCAN)
  ↓
Identifica centros (tópicos)
  ↓
Extrai palavras-chave (c-TF-IDF)
  ↓
Output: {Tópico 0, Tópico 1, ...}
```

Uso:
```bash
PYTHONPATH=. python3 src/nlp/bertopic_analyzer.py
```

Output exemplo:
```
7 tópicos encontrados
Tópico 0 (12 docs): enchente, alagamento, rua inundada
Tópico 1 (8 docs): seca, reservatório, falta água
Tópico -1 (2 docs): RUÍDO (outliers)
```

---

### Camada 4: Armazenamento
**Responsáveis:** `src/database/`

```
CSV local
    ↓
BigQuery Client
    ↓
┌──────────────────────────┐
│  Dataset: pcj_monitoramento
│  ├─ Tabela: ocorrencias
│  └─ Views (6):
│     ├─ vw_ocorrencias_dashboard
│     ├─ vw_ocorrencias_relevantes
│     ├─ vw_indicadores_gerais
│     ├─ vw_risco_por_categoria
│     ├─ vw_risco_por_periodo
│     └─ vw_fontes
└──────────────────────────┘
```

**Arquivos:**

1. **schemas.py** — Define estrutura de dados
   ```python
   OCORRENCIAS_SCHEMA = [
       ("id", "STRING"),
       ("titulo", "STRING"),
       ("url", "STRING"),
       ("fonte_nome", "STRING"),
       ("relevante_pcj", "BOOLEAN"),
       ("categoria", "STRING"),
       ("nivel_risco", "INTEGER"),
       # ... mais 20 campos
   ]
   ```

2. **bigquery_client.py** — Cliente GCP
   ```python
   bq = BigQueryClient()
   bq.criar_dataset_se_nao_existir()
   bq.criar_tabela_ocorrencias_se_nao_existir()
   bq.enviar_csv(caminho_csv)
   ```

3. **views.py** — SQL para analytics
   ```python
   views_sql = get_views_sql(project_id, dataset_id, "ocorrencias")
   # Retorna 6 CREATE VIEW statements
   ```

**Deduplicação:**

A tabela principal usa `WRITE_APPEND` (append simples). Deduplicação acontece nas views:

```sql
-- vw_ocorrencias_dashboard
SELECT *
FROM (
  SELECT *,
  ROW_NUMBER() OVER (PARTITION BY id ORDER BY data_processamento DESC) as rn
  FROM `ocorrencias`
)
WHERE rn = 1  -- Pega apenas versão mais recente
```

---

### Camada 5: Visualização
**Responsáveis:** Dashboard Looker Studio (externo)

```
BigQuery Views
    ↓
Looker Studio
    ↓
3 Páginas:
├─ Visão Geral (KPIs + série temporal)
├─ Ocorrências Relevantes (tabela filtrada)
└─ Qualidade e Fontes (distribuição)
```

---

## Pipeline de Dados

### Fluxo Completo

```
[Fonte: G1 Campinas]
       ↓ Coleta (30 links)
[Lista URLs]
       ↓ Extração (per notícia: 5-30 seg)
[Textos brutos]
       ↓ Limpeza + Normalization
[Textos limpos]
       ↓ Relevância PCJ (termos + embeddings)
[Relevante? BOOLEAN]
       ↓ Classificação (categoria + risco)
[Categoria, Risco, Justificativa]
       ↓ Deduplicação + Padronização
[CSV pronto]
       ↓ Envio BigQuery (batch)
[BigQuery ocorrencias]
       ↓ Views SQL
[6 Views analíticas]
       ↓ Looker atualiza
[Dashboard ao vivo]
```

### Timings

```
Operação                   Tempo      Parallelizável?
────────────────────────────────────────────────────
Coleta (30 links)          ~10s       Não
Extração (30 notícias)     ~2min      Não (respeito ao servidor)
Limpeza                    ~1s        Sim
Classificação IA           ~5s        Sim (batch embeddings)
Formatação + CSV           ~1s        Sim
Envio BigQuery             ~2s        -
────────────────────────────────────────────────────
Total                      ~3min
```

---

## Módulos Python

### `src/config/settings.py`
Define paths e configurações globais.

```python
BASE_DIR           # Raiz do projeto
DATA_DIR          # data/
RAW_DATA_DIR      # data/raw/
PROCESSED_DATA_DIR # data/processed/

carregar_fontes()  # Lê config/fontes.yaml
```

### `src/collectors/`
- `base_collector.py` — Interface abstrata
- `bs4_collector.py` — Web scraping HTML
- `news_extractor.py` — Parsing de notícia individual

### `src/processing/`
- `cleaner.py` — Limpeza de texto
- `relevance_filter.py` — Filtro PCJ + embeddings
- `occurrence_formatter.py` — Padronização de campos

### `src/nlp/`
- `risk_classifier.py` — Classificação por embeddings
- `bertopic_analyzer.py` — Discovery de tópicos

### `src/database/`
- `schemas.py` — Definição de tipos BigQuery
- `bigquery_client.py` — Cliente GCP
- `views.py` — SQL para views analíticas

### `src/utils/`
- `file_handler.py` — Salvamento de CSV

### `src/main.py`
Pipeline principal que orquestra tudo.

---

## Modelos de IA

### 1. Sentence Transformers

**Modelo:** `paraphrase-multilingual-MiniLM-L12-v2`

**Por que:**
- Multilíngue (português + outros idiomas)
- Rápido (MiniLM)
- Overhead baixo (384 dims)
- Bom para semântica

**Como usar:**
```python
from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Calcular similaridade
from sklearn.metrics.pairwise import cosine_similarity
emb1 = modelo.encode("Enchente em Piracicaba")
emb2 = modelo.encode("Alagamento no rio PCJ")
sim = cosine_similarity([emb1], [emb2])[0][0]  # 0.8+ = similar
```

### 2. BERTopic

**O que faz:** Agrupa documentos por tópicos automaticamente

**Parâmetros:**
```python
BERTopic(
    embedding_model=transformer,      # Qual modelo de embedding
    vectorizer_model=vectorizer,      # Como extrair palavras-chave
    min_topic_size=3,                 # Mínimo docs por tópico
    nr_topics="auto",                 # Deixar automático
    calculate_probabilities=True,     # Calcular confiança
    verbose=True                      # Mostrar progresso
)
```

**Output:**
```python
topicos, probs = modelo.fit_transform(textos)
# topicos: [0, 1, -1, 0, 2, ...]  (id tópico por doc)
# probs: [[0.8, 0.1, 0.1], ...]   (confiança por tópico)

info = modelo.get_topic_info()
# DataFrame com: Topic | Count | Name (palavras-chave)

palavras = modelo.get_topic(0)
# [(palavra, peso), ...] top-N palavras do tópico
```

---

## BigQuery e Views

### Tabela Principal: `ocorrencias`

```sql
CREATE TABLE `projeto.dataset.ocorrencias` (
  id STRING,
  titulo STRING,
  url STRING,
  fonte_nome STRING,
  fonte_url STRING,
  data_coleta TIMESTAMP,
  
  titulo_extraido STRING,
  subtitulo STRING,
  texto_original STRING,
  texto_limpo STRING,
  erro_extracao STRING,
  
  relevante_pcj BOOLEAN,
  termos_pcj STRING,
  termos_hidricos STRING,
  termos_exclusao STRING,
  
  categoria STRING,
  evento_principal STRING,
  nivel_risco INTEGER,
  justificativa_risco STRING,
  
  metodo_classificacao STRING,
  data_processamento TIMESTAMP
);
```

**Índices recomendados:**
- `id` (deduplicação)
- `data_processamento` (timeseries)
- `nivel_risco` (filtros)
- `categoria` (agregação)

### Views Analíticas

**1. vw_ocorrencias_dashboard**
```sql
-- Base para dashboard, com deduplicação
SELECT * EXCEPT(rn) FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY data_processamento DESC) rn
  FROM ocorrencias
) WHERE rn = 1;
```

**2. vw_ocorrencias_relevantes**
```sql
SELECT * FROM vw_ocorrencias_dashboard WHERE relevante_pcj = TRUE;
```

**3. vw_indicadores_gerais**
```sql
SELECT
  COUNT(*) as total,
  COUNTIF(relevante_pcj) as relevantes,
  COUNTIF(NOT relevante_pcj) as irrelevantes,
  MAX(data_processamento) as ultima_atualizacao
FROM vw_ocorrencias_dashboard;
```

**4. vw_risco_por_categoria**
```sql
SELECT
  categoria,
  nivel_risco,
  COUNT(*) as total
FROM vw_ocorrencias_dashboard
WHERE relevante_pcj = TRUE
GROUP BY 1, 2
ORDER BY 1, 2;
```

**5. vw_risco_por_periodo**
```sql
SELECT
  DATE(data_processamento) as data,
  categoria,
  nivel_risco,
  COUNT(*) as total
FROM vw_ocorrencias_dashboard
WHERE relevante_pcj = TRUE
GROUP BY 1, 2, 3
ORDER BY 1 DESC;
```

**6. vw_fontes**
```sql
SELECT
  fonte_nome,
  COUNT(*) as total,
  COUNTIF(relevante_pcj) as relevantes,
  MAX(data_processamento) as ultima_coleta
FROM vw_ocorrencias_dashboard
GROUP BY 1
ORDER BY 2 DESC;
```

---

## Como Estender

### Adicionar Nova Fonte

1. Editar `src/config/fontes.yaml`:
```yaml
fontes:
  - nome: "Folha Campinas"
    url_base: "https://folha.uol.com.br/..."
    tipo: "site"
    ativa: true
```

2. Testar com `teste_fontes.py`

3. Se padrão HTML é diferente, criar novo coletor em `src/collectors/`

### Melhorar Classificação

**Opção 1:** Adicionar mais regras (rápido)
```python
# src/nlp/risk_classifier.py
if "barragem" in texto and "rompimento" in texto:
    return {
        "categoria": "alerta_defesa_civil",
        "nivel_risco": 5,  # Crítico!
        "justificativa": "Possível rompimento de barragem"
    }
```

**Opção 2:** Fine-tuning de modelo (mais complexo)
```python
# Treinar modelo customizado
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

exemplos = [
    InputExample(texts=["enchente em Piracicaba", "alagamento no rio"], label=0),
    InputExample(texts=["seca severa", "falta de água"], label=1),
    # ... mais exemplos
]

modelo = SentenceTransformer("...")
train_dataloader = DataLoader(exemplos, shuffle=True, batch_size=16)
modelo.fit(train_dataloader, epochs=1, warmup_steps=100)
```

### Adicionar Novo Campo

1. Adicionar a `OCORRENCIAS_SCHEMA` em `src/database/schemas.py`
2. Atualizar pipeline para popular o campo
3. Recrear views (ou adicionar coluna à view)

---

## Troubleshooting

### "Nenhum CSV encontrado"
```
Solução: Rode o pipeline primeiro
python -m src.main
```

### "Erro de conexão BigQuery"
```
Verificar:
1. Variável GOOGLE_APPLICATION_CREDENTIALS aponta para arquivo JSON?
2. Arquivo JSON existe e é válido?
3. Credenciais têm permissão BigQuery?

set GOOGLE_APPLICATION_CREDENTIALS=C:\caminho\para\chave.json
```

### "Taxa de erro alta na classificação"
```
Possíveis causas:
1. Poucos exemplos de treinamento (BERTopic requer ~20+ docs)
2. Textos muito curtos (<50 caracteres)
3. Fonte com padrão muito diferente

Verificar: tail -50 data/raw/pipeline_bruto_*.csv
```

### "BERTopic lento"
```
Dicas:
1. Reduzir min_topic_size (cluster menor = mais rápido)
2. Usar GPU: CUDA_VISIBLE_DEVICES=0 python ...
3. Reduzir nr_words (menos palavras-chave)

benchmark:
- 100 docs: ~30 seg
- 500 docs: ~2 min
- 5000 docs: ~15 min
```

### "Dashboard não atualiza"
```
Checklist:
1. Dados foram enviados para BigQuery? (verificar tabela)
2. Views foram recriadas? (python teste_bigquery_criar_views.py)
3. Link do Looker aponta para dataset correto?
4. Permissões Looker ↔ BigQuery? (admin Google Cloud)
```

---

**Fim da Documentação Técnica**
