# QUICK_SETUP.md — Guia Rápido para Replicar o Projeto

## ⚡ Setup em 5 Passos (15 min)

### Pré-requisitos
- Python 3.12
- Git
- Conta Google Cloud (para BigQuery)

---

## PASSO 1: Clonar e Preparar (2 min)

```bash
# Clonar repositório
git clone https://github.com/NPLaura22/PI_V_MonitoramentoBaciasPCJ.git
cd PI_V_MonitoramentoBaciasPCJ/PI_V_MonitoramentoBaciasPCJ

# Criar ambiente virtual
python -m venv .venv

# Ativar (macOS/Linux)
source .venv/bin/activate

# Ativar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Se erro de permissão no PowerShell, executar ANTES:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## PASSO 2: Instalar Dependências (3 min)

```bash
# Atualizar pip
python -m pip install --upgrade pip setuptools wheel

# Instalar dependências básicas
pip install -r requirements.txt

# Ou por etapas se houver problema:
pip install beautifulsoup4 requests pandas numpy python-dotenv feedparser lxml pyyaml dateparser
pip install google-cloud-bigquery pandas-gbq
pip install transformers sentence-transformers bertopic scikit-learn spacy
```

---

## PASSO 3: Configurar Credenciais (3 min)

### A. Criar arquivo `.env`

```bash
# Copiar template
cp .env.example .env

# Editar .env com seus dados
nano .env
# ou usar seu editor: VS Code, Sublime, etc
```

### B. Conteúdo do `.env`

```env
GOOGLE_CLOUD_PROJECT_ID=seu-projeto-gcp
BIGQUERY_DATASET=pcj_monitoramento
BIGQUERY_TABLE_OCORRENCIAS=ocorrencias
GOOGLE_APPLICATION_CREDENTIALS=/caminho/completo/para/credencial.json
ENVIAR_PARA_BIGQUERY=false
```

### C. Adicionar Credencial JSON

```bash
# Criar pasta
mkdir -p credentials

# Copiar seu arquivo JSON do Google Cloud
# (Baixar em: Google Cloud Console → Service Account → Create Key)
cp ~/Downloads/seu-projeto-key.json credentials/pcj-bigquery-key.json

# Atualizar path no .env
GOOGLE_APPLICATION_CREDENTIALS=/Users/seu-user/Caminho/Do/Projeto/credentials/pcj-bigquery-key.json
```

> ⚠️ **NÃO subir credentials/ para Git** — já está no `.gitignore`

---

## PASSO 4: Testar Ambiente (4 min)

```bash
# Teste 1: Verificar bibliotecas
python teste_ambiente.py

# Esperado: "✅ Todas as bibliotecas estão instaladas"

# Teste 2: Verificar configuração de fontes
python teste_fontes.py

# Esperado: "Fontes ativas carregadas: 1" (ou mais)

# Teste 3: Verificar BigQuery (se ENVIAR_PARA_BIGQUERY=true)
python teste_bigquery_conexao.py

# Esperado: "Conexão com BigQuery validada com sucesso."
```

---

## PASSO 5: Rodar o Pipeline (3 min)

### Opção A: Modo Local (sem enviar BigQuery)

```bash
# Editar .env
ENVIAR_PARA_BIGQUERY=false

# Rodar pipeline
python -m src.main

# Output:
# Coletando: G1 Campinas e Regiao
# 30 notícias encontradas
# Processando: Título da notícia...
# ...
# Total processado: 30
# Total relevante para PCJ: 15
# CSV salvo em: data/raw/pipeline_bruto_20260531_143022.csv
```

### Opção B: Modo BigQuery (enviar dados)

```bash
# Editar .env
ENVIAR_PARA_BIGQUERY=true

# Rodar pipeline
python -m src.main

# Output:
# ...
# Enviando dados para o BigQuery...
# Envio para BigQuery concluído com sucesso.
```

---

## 🎉 Pronto!

Você agora tem:
- ✅ Pipeline rodando localmente
- ✅ Dados sendo coletados e processados
- ✅ BigQuery pronto (se configurado)
- ✅ Dashboard alimentado (se enviado para BQ)

---

## Próximos Passos

### Analisar Resultados

```bash
# Ver dados processados (último CSV)
head -3 data/raw/pipeline_bruto_*.csv | column -t -s ';'

# Rodar BERTopic (descobrir tópicos)
python demo_bertopic_quick.py

# Ver resumo do pipeline
python demo_pipeline_summary.py
```

### Acessar Dashboard

Se `ENVIAR_PARA_BIGQUERY=true`:

1. Abrir [Looker Studio Link do projeto]
2. Filtrar por período, categoria, risco
3. Ver insights em tempo real

### Adicionar Mais Fontes

Edit `src/config/fontes.yaml`:

```yaml
fontes:
  - nome: "G1 Campinas e Regiao"
    url_base: "https://g1.globo.com/sp/campinas-regiao/"
    ativa: true
    
  - nome: "Folha Campinas"  # ← NOVO
    url_base: "https://folha.uol.com.br/especial/..."
    ativa: false  # Ativar depois de testar
    tipo: "site"
```

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError: No module named 'sentence_transformers'" | `pip install sentence-transformers` |
| "Erro: GOOGLE_APPLICATION_CREDENTIALS não encontrado" | Verificar path no `.env` — deve ser **absoluto** |
| "Nenhum dado no BigQuery após pipeline" | Verificar `ENVIAR_PARA_BIGQUERY=true` no `.env` |
| "BERTopic muito lento" | Rodar com menos notícias primeiro (teste_classificacao_amostras.py) |
| ".env file not found" | `cp .env.example .env` e editar |

---

## Estrutura de Diretórios Esperada

```
PI_V_MonitoramentoBaciasPCJ/
├── .env                    ← Suas credenciais (NÃO subir)
├── .venv/                  ← Ambiente virtual (NÃO subir)
├── credentials/            ← Chaves JSON (NÃO subir)
│   └── pcj-bigquery-key.json
├── data/
│   ├── raw/
│   │   └── pipeline_bruto_*.csv
│   ├── processed/
│   └── samples/
├── src/
│   ├── collectors/
│   ├── config/
│   ├── database/
│   ├── nlp/
│   ├── processing/
│   ├── utils/
│   └── main.py
├── requirements.txt
├── demo_pipeline_summary.py
├── demo_bertopic_quick.py
├── PRESENTATION_20MIN.md
├── ARCHITECTURE.md
├── QUICK_SETUP.md (← você está aqui)
└── ... outros arquivos
```

---

## Comandos Úteis

```bash
# Ativar venv
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Desativar venv
deactivate

# Ver arquivos generados
ls -la data/raw/

# Ver últimas 100 linhas de um CSV
tail -100 data/raw/pipeline_bruto_*.csv

# Contar notícias
wc -l data/raw/pipeline_bruto_*.csv

# Rodar com output detalhado
PYTHONPATH=. python3 src/nlp/bertopic_analyzer.py 2>&1 | tee log_bertopic.txt

# Testar apenas classificação
python teste_classificacao_amostras.py
```

---

## Suporte

- 📖 Documentação completa: `ARCHITECTURE.md`
- 🎯 Roteiro apresentação: `PRESENTATION_20MIN.md`
- 💻 Código: GitHub - `src/main.py`
- 🐛 Issues: Abrir issue no GitHub

---

**Boa sorte! 🚀**
