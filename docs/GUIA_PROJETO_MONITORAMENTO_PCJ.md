# Guia do Projeto — Monitoramento Hídrico das Bacias PCJ

Este documento explica a estrutura do projeto, a função de cada arquivo, como rodar o sistema em outro computador e como compartilhar os acessos do Google Cloud BigQuery e do Looker/Data Studio com os demais integrantes do grupo.

---

## 1. Visão geral do projeto

O projeto tem como objetivo coletar notícias, tratar os dados, identificar ocorrências relacionadas às Bacias PCJ e disponibilizar os resultados em um dashboard no Looker/Data Studio.

Fluxo principal:

```text
Coleta de notícias
→ Extração do corpo da notícia
→ Limpeza do texto
→ Filtro de relevância PCJ
→ Classificação de categoria
→ Classificação de risco
→ Salvamento em CSV
→ Envio para BigQuery
→ Visualização no Looker/Data Studio
```

Tecnologias utilizadas:

```text
Python
BeautifulSoup
Requests
Pandas
Google BigQuery
Looker/Data Studio
Regras determinísticas de classificação
Estrutura preparada para futura inclusão de IA, embeddings, NER, BERTopic e Hugging Face
```

---

## 2. Estrutura geral de pastas

A estrutura atual do projeto está organizada aproximadamente assim:

```text
monitoramento-pcj/
│
├── .venv/
├── credentials/
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── notebooks/
│
├── src/
│   ├── collectors/
│   ├── config/
│   ├── dashboard/
│   ├── database/
│   ├── nlp/
│   ├── processing/
│   └── utils/
│
├── tests/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── teste_ambiente.py
├── teste_fontes.py
├── teste_coleta.py
├── teste_classificacao_amostras.py
├── teste_bigquery_conexao.py
├── teste_bigquery_envio_csv.py
├── teste_bigquery_criar_views.py
└── enviar_amostras_bigquery.py
```

---

## 3. Explicação das principais pastas

### `.venv/`

Pasta do ambiente virtual Python.

Ela contém as bibliotecas instaladas apenas para este projeto.

Importante:

```text
Não subir essa pasta para o GitHub.
Cada integrante deve criar a própria .venv no computador.
```

---

### `credentials/`

Pasta onde fica a chave JSON da conta de serviço do Google Cloud.

Exemplo:

```text
credentials/pcj-bigquery-key.json
```

Importante:

```text
Não subir essa pasta para o GitHub.
Não compartilhar essa chave em grupo público.
Não enviar a chave em prints.
```

Essa pasta é ignorada pelo `.gitignore`.

---

### `data/raw/`

Guarda arquivos brutos gerados pelo pipeline.

Exemplos:

```text
pipeline_bruto_20260427_095711.csv
pipeline_relevante_20260427_095711.csv
coleta_g1_campinas_bruto_...
```

Uso:

```text
Armazenar resultados da coleta e processamento local.
Servir como backup local antes do envio ao BigQuery.
```

---

### `data/processed/`

Guarda dados já processados, classificados ou simulados.

Exemplos:

```text
resultado_classificacao_simulada_...
amostras_simuladas_bigquery_...
```

Uso:

```text
Guardar resultados de testes de classificação.
Guardar amostras simuladas processadas antes do envio ao BigQuery.
```

---

### `data/samples/`

Guarda dados de exemplo ou simulação usados para testar o sistema.

Exemplo:

```text
noticias_pcj_simuladas.csv
```

Uso:

```text
Permitir testar as regras sem depender de o G1 publicar notícias hídricas no dia.
```

---

### `src/`

Pasta principal do código-fonte.

Todo o código mais importante do sistema fica dentro dela.

---

## 4. Explicação dos arquivos principais

## 4.1 Arquivos de configuração

### `src/config/settings.py`

Responsável por definir caminhos principais do projeto.

Funções e variáveis importantes:

```python
BASE_DIR
DATA_DIR
RAW_DATA_DIR
PROCESSED_DATA_DIR
FONTES_CONFIG_PATH
carregar_fontes()
```

Esse arquivo permite que o projeto encontre corretamente as pastas `data/raw`, `data/processed` e o arquivo de fontes.

---

### `src/config/fontes.yaml`

Arquivo que lista as fontes monitoradas.

Exemplo:

```yaml
fontes:
  - nome: "G1 Campinas e Regiao"
    url_base: "https://g1.globo.com/sp/campinas-regiao/"
    tipo: "site"
    ativa: true
```

No momento, o pipeline principal está usando o G1 Campinas e Região.

Futuramente, novas fontes podem ser adicionadas nesse arquivo.

---

## 4.2 Coletores

### `src/collectors/base_collector.py`

Classe base para os coletores.

Ela define um modelo que os coletores devem seguir.

Contém:

```python
class BaseCollector(ABC)
```

Função principal:

```python
coletar()
```

Esse arquivo não coleta notícias sozinho. Ele serve como estrutura para os coletores específicos.

---

### `src/collectors/bs4_collector.py`

Coletor genérico usando:

```text
requests
BeautifulSoup
```

Função:

```text
Acessa uma página de notícias, lê o HTML e encontra possíveis links de notícias.
```

Ele filtra links para evitar:

```text
vídeos
playlists
globoplay
futebol
podcasts
links que não terminam com .ghtml
```

Classe principal:

```python
BS4Collector
```

Uso no pipeline:

```python
coletor = BS4Collector(
    nome_fonte="G1 Campinas e Regiao",
    url_base="https://g1.globo.com/sp/campinas-regiao/"
)
```

---

### `src/collectors/news_extractor.py`

Responsável por entrar dentro de cada notícia e extrair:

```text
título extraído
subtítulo
corpo completo da notícia
erro de extração, se houver
```

Classe principal:

```python
NewsExtractor
```

Função principal:

```python
extrair(url)
```

O resultado é usado depois na limpeza, no filtro de relevância e na classificação de risco.

---

## 4.3 Processamento

### `src/processing/cleaner.py`

Responsável por limpar o texto extraído das notícias.

Remove:

```text
rodapés do G1
chamadas recomendadas
linhas muito curtas
legendas de foto
espaços extras
```

Função principal:

```python
limpar_texto_noticia(texto)
```

Campos gerados no pipeline:

```text
texto_original
texto_limpo
```

`texto_original` guarda o conteúdo bruto da notícia.

`texto_limpo` guarda o texto tratado, usado para classificação.

---

### `src/processing/relevance_filter.py`

Responsável por identificar se uma notícia é relevante para as Bacias PCJ.

Ele procura dois grupos de termos:

```text
termos geográficos PCJ
termos hídricos/eventos ambientais
```

Exemplos de termos geográficos:

```text
PCJ
Campinas
Piracicaba
Capivari
Jundiaí
Atibaia
Morungaba
```

Exemplos de termos hídricos:

```text
chuva
alagamento
enchente
seca
estiagem
abastecimento
contaminação
rio
manancial
Defesa Civil
CEMADEN
```

Também possui termos de exclusão para evitar falsos positivos:

```text
mega-sena
quina
apostas
futebol
olimpíada de matemática
```

Funções principais:

```python
calcular_relevancia_pcj(titulo, texto_original)
explicar_relevancia_pcj(titulo, texto_original)
```

A função `explicar_relevancia_pcj` é muito útil porque retorna:

```text
se é relevante
quais termos PCJ foram encontrados
quais termos hídricos foram encontrados
quais termos de exclusão foram encontrados
```

---

### `src/processing/occurrence_formatter.py`

Padroniza os campos antes de salvar no CSV ou enviar para o BigQuery.

Funções principais:

```python
gerar_id_ocorrencia(url, titulo)
padronizar_ocorrencia(noticia)
```

A função `gerar_id_ocorrencia` cria um ID único baseado na URL e no título.

Esse ID é usado para evitar duplicidades nas views do BigQuery.

Campos finais padronizados:

```text
id
titulo
url
fonte_nome
fonte_url
data_coleta
titulo_extraido
subtitulo
texto_original
texto_limpo
erro_extracao
relevante_pcj
termos_pcj
termos_hidricos
termos_exclusao
categoria
evento_principal
nivel_risco
justificativa_risco
metodo_classificacao
data_processamento
```

---

## 4.4 Classificação e risco

### `src/nlp/risk_classifier.py`

Responsável por classificar:

```text
categoria
evento principal
nível de risco
justificativa do risco
método de classificação
```

Funções principais:

```python
classificar_categoria(texto)
extrair_evento_principal(texto)
classificar_nivel_risco(texto, relevante_pcj)
gerar_justificativa(...)
analisar_risco(texto, relevante_pcj)
```

Categorias atuais:

```text
enchente_alagamento
estiagem_seca
contaminacao_poluicao
abastecimento
alerta_defesa_civil
monitoramento_hidrico
irrelevante
```

Escala de risco:

```text
0 = irrelevante
1 = informativo
2 = atenção
3 = moderado
4 = alto
5 = crítico
```

No momento, a classificação é feita por regras determinísticas.

Isso é importante porque:

```text
é explicável
é auditável
facilita a apresentação
serve como base antes de incluir IA
```

Futuramente, essa camada pode ser complementada com:

```text
Hugging Face
text classification
embeddings
NER
BERTopic
event extraction
```

---

## 4.5 BigQuery

### `src/database/schemas.py`

Define o schema da tabela `ocorrencias` no BigQuery.

Campo principal:

```python
OCORRENCIAS_SCHEMA
```

Esse schema informa ao BigQuery os tipos dos campos:

```text
STRING
BOOLEAN
INTEGER
TIMESTAMP
```

---

### `src/database/bigquery_client.py`

Cliente responsável por conversar com o BigQuery.

Classe principal:

```python
BigQueryClient
```

Funções principais:

```python
criar_dataset_se_nao_existir()
criar_tabela_ocorrencias_se_nao_existir()
preparar_dataframe_ocorrencias(df)
enviar_dataframe(df)
enviar_csv(caminho_csv)
```

Essa classe:

```text
lê as variáveis do .env
configura a credencial JSON
cria dataset
cria tabela
prepara tipos de dados
envia DataFrame/CSV para o BigQuery
```

---

### `src/database/views.py`

Gera os comandos SQL para criar views analíticas no BigQuery.

Função principal:

```python
get_views_sql(project_id, dataset_id, table_ocorrencias)
```

Views criadas:

```text
vw_ocorrencias_dashboard
vw_ocorrencias_relevantes
vw_indicadores_gerais
vw_risco_por_categoria
vw_risco_por_periodo
vw_fontes
```

Essas views são usadas pelo Looker/Data Studio.

---

## 4.6 Utilitários

### `src/utils/file_handler.py`

Responsável por salvar listas de dicionários em CSV.

Função principal:

```python
salvar_csv(dados, caminho_arquivo)
```

Usa separador `;` porque o Excel em português/Windows reconhece melhor.

---

## 4.7 Pipeline principal

### `src/main.py`

Arquivo principal do projeto.

Para rodar:

```powershell
python -m src.main
```

Ele executa:

```text
coleta
extração
limpeza
relevância PCJ
categoria
risco
padronização
salvamento em CSV
envio opcional para BigQuery
```

O envio para BigQuery depende da variável:

```env
ENVIAR_PARA_BIGQUERY=true
```

Se estiver:

```env
ENVIAR_PARA_BIGQUERY=false
```

o pipeline roda localmente e não envia dados para o BigQuery.

---

## 5. Arquivos de teste e apoio

### `teste_ambiente.py`

Testa se as bibliotecas básicas estão instaladas corretamente.

Rodar:

```powershell
python teste_ambiente.py
```

---

### `teste_fontes.py`

Testa a leitura do arquivo:

```text
src/config/fontes.yaml
```

Rodar:

```powershell
python teste_fontes.py
```

---

### `teste_coleta.py`

Arquivo usado durante o desenvolvimento para testar coleta, extração, limpeza e classificação.

Hoje o pipeline principal está em:

```text
src/main.py
```

Mas esse arquivo ainda pode ser útil para testes manuais.

Rodar:

```powershell
python teste_coleta.py
```

---

### `teste_classificacao_amostras.py`

Testa a classificação usando notícias simuladas salvas em:

```text
data/samples/noticias_pcj_simuladas.csv
```

Rodar:

```powershell
python teste_classificacao_amostras.py
```

Gera resultado em:

```text
data/processed/
```

---

### `teste_bigquery_conexao.py`

Testa se o Python consegue conectar ao BigQuery, criar dataset e criar tabela.

Rodar:

```powershell
python teste_bigquery_conexao.py
```

Resultado esperado:

```text
Dataset pronto...
Tabela pronta...
Conexão com BigQuery validada com sucesso.
```

---

### `teste_bigquery_envio_csv.py`

Envia o CSV `pipeline_bruto_*.csv` mais recente para o BigQuery.

Rodar:

```powershell
python teste_bigquery_envio_csv.py
```

Hoje o `src/main.py` já pode enviar automaticamente, mas esse teste continua útil.

---

### `teste_bigquery_criar_views.py`

Cria ou atualiza as views analíticas do BigQuery.

Rodar:

```powershell
python teste_bigquery_criar_views.py
```

Usado quando `src/database/views.py` for alterado.

---

### `enviar_amostras_bigquery.py`

Cria notícias simuladas, processa com as mesmas regras do pipeline e envia para o BigQuery.

Rodar:

```powershell
python enviar_amostras_bigquery.py
```

Uso:

```text
enriquecer o dashboard com dados fictícios realistas para validação visual e apresentação.
```

Importante:

```text
Os registros da Fonte Simulada devem ser explicados como dados de teste.
```

---

## 6. Como rodar o projeto em outro computador

### 6.1 Pré-requisitos

Cada integrante precisa ter instalado:

```text
Python 3.12
VS Code
Git
Conta Google com acesso ao projeto Google Cloud
```

Versão recomendada:

```text
Python 3.12
```

Evitar Python 3.14 por enquanto, porque algumas bibliotecas de IA e dados podem ainda não estar totalmente estáveis nessa versão.

---

### 6.2 Clonar o repositório

No computador do integrante, abrir o terminal e rodar:

```powershell
git clone LINK_DO_REPOSITORIO
cd monitoramento-pcj
```

Exemplo:

```powershell
git clone https://github.com/usuario/monitoramento-pcj.git
cd monitoramento-pcj
```

---

### 6.3 Criar ambiente virtual

Na raiz do projeto:

```powershell
py -3.12 -m venv .venv
```

Ativar no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se aparecer erro de permissão no PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois tentar novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Quando funcionar, o terminal deve mostrar:

```text
(.venv) PS ...
```

---

### 6.4 Instalar dependências

Com a `.venv` ativada:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Se houver problema com bibliotecas muito pesadas, instalar por etapas:

```powershell
pip install beautifulsoup4 requests pandas numpy python-dotenv feedparser lxml pyyaml dateparser
pip install google-cloud-bigquery pandas-gbq
```

As bibliotecas de IA podem ser instaladas depois, conforme necessidade:

```powershell
pip install transformers sentence-transformers torch bertopic scikit-learn spacy
```

---

### 6.5 Criar arquivo `.env`

Copiar o `.env.example` e criar um arquivo chamado:

```text
.env
```

Exemplo:

```env
GOOGLE_CLOUD_PROJECT_ID=monitoramento-pcj-494612
BIGQUERY_DATASET=pcj_monitoramento
BIGQUERY_TABLE_OCORRENCIAS=ocorrencias
GOOGLE_APPLICATION_CREDENTIALS=C:\CAMINHO\DO\PROJETO\credentials\pcj-bigquery-key.json
ENVIAR_PARA_BIGQUERY=true
```

Cada integrante precisa ajustar o caminho da credencial JSON no próprio computador.

Exemplo de caminho:

```env
GOOGLE_APPLICATION_CREDENTIALS=C:\Faculdade\QUINTO SEMESTRE\Projeto Integrador V\monitoramento-pcj\credentials\pcj-bigquery-key.json
```

---

### 6.6 Colocar credencial JSON

Criar a pasta:

```text
credentials/
```

Colocar dentro dela o arquivo:

```text
pcj-bigquery-key.json
```

Importante:

```text
Esse arquivo não deve ser enviado para o GitHub.
Ele deve ser compartilhado apenas de forma segura, se necessário.
```

O ideal é cada integrante gerar a própria chave ou usar acesso individual pelo Google Cloud.

---

### 6.7 Testar ambiente

Rodar:

```powershell
python teste_ambiente.py
```

Depois:

```powershell
python teste_fontes.py
```

Depois testar BigQuery:

```powershell
python teste_bigquery_conexao.py
```

---

### 6.8 Rodar pipeline principal

Para rodar coleta + processamento + envio ao BigQuery:

```powershell
python -m src.main
```

Se `ENVIAR_PARA_BIGQUERY=true`, o pipeline enviará os dados ao BigQuery.

Se quiser rodar somente localmente:

```env
ENVIAR_PARA_BIGQUERY=false
```

Depois rodar:

```powershell
python -m src.main
```

---

Sugestão:

```text
Dar acesso de Editor ao dashboard para todos que vão mexer no layout.
Dar acesso BigQuery Data Viewer + Job User para quem precisa consultar dados.
Dar acesso BigQuery Data Editor + Job User apenas para quem vai rodar scripts que enviam dados.
```

---

## 9. Dashboard no Looker/Data Studio

O dashboard criado possui 3 páginas principais.

---

### Página 1 — Visão Geral

Objetivo:

```text
Mostrar a visão geral do monitoramento.
```

Elementos:

```text
Cards:
- Total de ocorrências
- Relevantes PCJ
- Irrelevantes
- Risco moderado+
- Risco alto/crítico

Gráficos:
- Ocorrências por categoria
- Evolução das ocorrências por período

Tabela:
- Últimas ocorrências monitoradas
```

Fonte principal:

```text
vw_ocorrencias_dashboard
```

Outras fontes usadas:

```text
vw_indicadores_gerais
vw_risco_por_categoria
vw_risco_por_periodo
```

---

### Página 2 — Ocorrências Relevantes

Objetivo:

```text
Mostrar apenas as ocorrências classificadas como relevantes para o projeto.
```

Elementos:

```text
Filtros:
- Período
- Categoria
- Nível de risco

Card:
- Total de ocorrências relevantes

Tabela:
- Data
- Título
- Fonte
- Categoria
- Evento
- Risco
- Justificativa
- Link
```

Fonte principal:

```text
vw_ocorrencias_relevantes
```

---

### Página 3 — Fontes e Qualidade dos Dados

Objetivo:

```text
Mostrar a origem dos dados e a qualidade da coleta/classificação.
```

Elementos:

```text
Cards:
- Total de fontes
- Total de ocorrências
- Relevantes PCJ
- Última coleta

Gráficos:
- Ocorrências por fonte
- Ocorrências relevantes por fonte

Tabela:
- Resumo das fontes monitoradas

Observação:
- Indicação de que a Fonte Simulada foi usada para validação visual do protótipo.
```

Fonte principal:

```text
vw_fontes
```

Outras fontes usadas:

```text
vw_indicadores_gerais
```

---

## 10. BigQuery: tabelas e views

Dataset:

```text
pcj_monitoramento
```

Tabela principal:

```text
ocorrencias
```

Views:

```text
vw_ocorrencias_dashboard
vw_ocorrencias_relevantes
vw_indicadores_gerais
vw_risco_por_categoria
vw_risco_por_periodo
vw_fontes
```

---

### `ocorrencias`

Tabela principal onde os dados são inseridos pelo Python.

---

### `vw_ocorrencias_dashboard`

View usada como base geral do dashboard.

Remove duplicatas usando:

```sql
ROW_NUMBER() OVER (
  PARTITION BY id
  ORDER BY data_processamento DESC
)
```

Assim, se a mesma notícia for enviada mais de uma vez, o dashboard mostra apenas a versão mais recente.

---

### `vw_ocorrencias_relevantes`

Mostra apenas:

```text
relevante_pcj = TRUE
```

Usada na Página 2.

---

### `vw_indicadores_gerais`

Gera os indicadores agregados:

```text
total_ocorrencias
total_relevantes_pcj
total_irrelevantes
total_risco_moderado_ou_maior
total_risco_alto_ou_critico
media_nivel_risco
ultima_data_coleta
total_fontes
```

Usada nos cards.

---

### `vw_risco_por_categoria`

Agrupa ocorrências por categoria.

Usada no gráfico:

```text
Ocorrências por categoria
```

---

### `vw_risco_por_periodo`

Agrupa ocorrências por data, categoria e risco.

Usada no gráfico:

```text
Evolução das ocorrências por período
```

---

### `vw_fontes`

Agrupa dados por fonte.

Usada na Página 3.

---

## 11. Cuidados importantes

### 11.1 Não subir credenciais

Nunca subir para o GitHub:

```text
.env
credentials/
*.json
.venv/
```

Esses itens devem estar no `.gitignore`.

---

### 11.2 Cuidado com duplicidade

Atualmente, o envio ao BigQuery usa `WRITE_APPEND`.

Isso significa:

```text
cada execução adiciona novas linhas na tabela ocorrencias
```

As views reduzem duplicidade no dashboard usando o campo `id`.

No futuro, pode ser implementado um `MERGE` no BigQuery para evitar duplicatas já na tabela principal.

---

### 11.3 Dados simulados

O projeto possui dados simulados para apresentação e teste visual.

Fonte simulada:

```text
Fonte Simulada
```

Esses dados foram enviados pelo script:

```text
enviar_amostras_bigquery.py
```

Eles servem para:

```text
testar visualmente o dashboard
validar categorias
validar níveis de risco
mostrar cenários que podem não aparecer no G1 no dia da apresentação
```

Na apresentação, deixar claro que são dados simulados.

---

## 12. Comandos úteis

Ativar ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Rodar pipeline principal:

```powershell
python -m src.main
```

Testar BigQuery:

```powershell
python teste_bigquery_conexao.py
```

Criar views:

```powershell
python teste_bigquery_criar_views.py
```

Enviar CSV mais recente:

```powershell
python teste_bigquery_envio_csv.py
```

Enviar amostras simuladas:

```powershell
python enviar_amostras_bigquery.py
```

Testar classificação simulada:

```powershell
python teste_classificacao_amostras.py
```

---

## 13. Como continuar o projeto

Próximas melhorias possíveis:

```text
Adicionar mais fontes reais
Adicionar RSS quando disponível
Criar tratamento melhor para duplicatas
Implementar NER com Hugging Face ou spaCy
Implementar embeddings para relevância semântica
Implementar BERTopic para descoberta de tópicos
Criar classificação com modelo Hugging Face
Criar MERGE no BigQuery para evitar duplicidade física
Melhorar nomes amigáveis das categorias no dashboard
Criar mapa por município
Adicionar tabela de municípios PCJ
Criar camada de logs de coleta
Automatizar execução diária do pipeline
```

---

## 14. Resumo para o grupo

O que já está pronto:

```text
Estrutura do projeto
Ambiente Python
Coleta de notícias do G1 Campinas
Extração do corpo da notícia
Limpeza do texto
Filtro de relevância PCJ
Classificador de categoria e risco
Geração de CSV
Conexão com BigQuery
Criação da tabela ocorrencias
Criação das views analíticas
Envio automático para BigQuery
Dashboard com 3 páginas
Dados simulados para validação visual
```

O que o grupo pode fazer agora:

```text
Melhorar o layout do dashboard
Adicionar novas fontes
Testar mais notícias
Ajustar regras de classificação
Implementar IA/NER/embeddings
Preparar apresentação final
```

---

## 15. Observação final

O projeto está estruturado para funcionar como um protótipo robusto de monitoramento hídrico baseado em notícias.

Mesmo com regras determinísticas no momento, a arquitetura já permite evoluir para técnicas mais avançadas de PLN/IA, como:

```text
Named Entity Recognition
Text Embeddings
Topic Detection
Text Classification
BERTopic
Hugging Face
Event Extraction
```

Isso significa que o projeto já possui uma base técnica sólida para continuar crescendo.
