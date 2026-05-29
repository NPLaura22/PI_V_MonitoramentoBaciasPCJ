# Guia de Configuração — Para os Integrantes do Grupo

## Monitoramento Hídrico das Bacias PCJ

Este guia explica tudo que você precisa fazer para rodar o projeto no seu computador do zero.

---

## Pré-requisitos

Antes de começar, instale:

- **Python 3.12** — [python.org/downloads](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)
- **VS Code** — [code.visualstudio.com](https://code.visualstudio.com/)

> Evite Python 3.14 por enquanto — algumas bibliotecas ainda não são totalmente estáveis nessa versão.

---

## Passo 1 — Clonar o repositório

```bash
git clone https://github.com/NPLaura22/PI_V_MonitoramentoBaciasPCJ.git
cd PI_V_MonitoramentoBaciasPCJ
```

---

## Passo 2 — Criar o ambiente virtual

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
```

Se aparecer erro de permissão no Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

O terminal vai mostrar `(venv)` no início da linha quando estiver ativo.

> O ambiente virtual precisa estar ativo sempre que for rodar o projeto. Se fechar o terminal, ative novamente com o comando acima.

---

## Passo 3 — Instalar as dependências

Com o `(venv)` ativo:

```bash
pip install -r requirements.txt
```

Pode demorar alguns minutos na primeira vez.

---

## Passo 4 — Criar o arquivo `.env`

**Mac/Linux:**
```bash
cp .env.example .env
```

**Windows:**
```powershell
copy .env.example .env
```

Abra o `.env` e preencha assim:

```
GOOGLE_CLOUD_PROJECT_ID=monitoramento-pcj-494612
BIGQUERY_DATASET=pcj_monitoramento
BIGQUERY_TABLE_OCORRENCIAS=ocorrencias
GOOGLE_APPLICATION_CREDENTIALS=/caminho/completo/para/credentials/pcj-bigquery-key.json
ENVIAR_PARA_BIGQUERY=false
```

Para saber o caminho exato, rode `pwd` no terminal dentro da pasta do projeto e adicione `/credentials/pcj-bigquery-key.json` ao final.

---

## Passo 5 — Colocar a credencial do Google Cloud

O arquivo `pcj-bigquery-key.json` não está no GitHub por segurança. Peça ao responsável do projeto por canal seguro.

Depois de receber:
1. Coloque dentro da pasta `credentials/`
2. Renomeie para `pcj-bigquery-key.json`
3. Atualize o caminho no `.env`

---

## Passo 6 — Testar o ambiente

```bash
PYTHONPATH=. python3 scripts/tests/teste_ambiente.py
PYTHONPATH=. python3 scripts/tests/teste_fontes.py
PYTHONPATH=. python3 scripts/tests/teste_bigquery_conexao.py
```

Resultado esperado do último:
```
Dataset pronto: monitoramento-pcj-494612:pcj_monitoramento
Tabela pronta: monitoramento-pcj-494612:pcj_monitoramento.ocorrencias
Conexão com BigQuery validada com sucesso.
```

---

## Passo 7 — Criar as views no BigQuery

Só precisa rodar uma vez (ou quando `src/database/views.py` for alterado):

```bash
PYTHONPATH=. python3 scripts/tests/teste_bigquery_criar_views.py
```

---

## Passo 8 — Rodar o pipeline

```bash
PYTHONPATH=. python3 -m src.main
```

Para enviar para o BigQuery, mude `ENVIAR_PARA_BIGQUERY=true` no `.env` antes de rodar.

---

## Passo 9 — Enviar dados simulados (opcional)

```bash
PYTHONPATH=. python3 scripts/demos/enviar_amostras_bigquery.py
```

---

## Comandos úteis

| Comando | O que faz |
|---|---|
| `PYTHONPATH=. python3 -m src.main` | Roda o pipeline completo |
| `PYTHONPATH=. python3 scripts/tests/teste_bigquery_conexao.py` | Testa conexão com BigQuery |
| `PYTHONPATH=. python3 scripts/tests/teste_bigquery_criar_views.py` | Cria/atualiza as views |
| `PYTHONPATH=. python3 scripts/tests/teste_bigquery_envio_csv.py` | Envia o CSV mais recente |
| `PYTHONPATH=. python3 scripts/tests/teste_coleta.py` | Testa só a coleta |
| `PYTHONPATH=. python3 src/nlp/bertopic_analyzer.py` | Análise exploratória de tópicos |

---

## Erros comuns

**`ModuleNotFoundError: No module named 'dotenv'`**
O venv não está ativo. Ative com `source venv/bin/activate` (Mac) ou `venv\Scripts\Activate.ps1` (Windows).

**`ModuleNotFoundError: No module named 'src'`**
Use sempre `PYTHONPATH=. python3 -m src.main`, nunca `python src/main.py`.

**`File pcj-bigquery-key.json was not found`**
O caminho no `.env` está errado. Rode `pwd` para pegar o caminho correto.

**`403 Access Denied`**
Seu email não tem permissão no projeto. Peça ao responsável para adicionar no Google Cloud IAM com os papéis `BigQuery Data Editor` e `BigQuery Job User`.

**`externally-managed-environment` ao rodar pip**
Crie e ative o `venv` primeiro antes de instalar as dependências.

---

## Estrutura do projeto

```
PI_V_MonitoramentoBaciasPCJ/
│
├── credentials/          ← pcj-bigquery-key.json (não vai pro GitHub)
├── data/
│   ├── raw/              ← CSVs gerados pelo pipeline
│   ├── processed/        ← CSVs de amostras processadas
│   └── samples/          ← dados de teste
│
├── scripts/
│   ├── tests/            ← scripts de teste e validação
│   ├── demos/            ← scripts de demonstração
│   └── utils/            ← utilitários auxiliares
│
├── src/
│   ├── collectors/       ← coleta de notícias
│   ├── config/           ← settings.py e fontes.yaml
│   ├── database/         ← BigQuery client, schema e views
│   ├── nlp/              ← embeddings, BERTopic e classificação
│   ├── processing/       ← limpeza, relevância e formatação
│   └── utils/            ← utilitários
│
├── .env                  ← configurações locais (não vai pro GitHub)
├── .env.example          ← modelo do .env
└── requirements.txt      ← dependências Python
```

---

## Dashboard no Looker Studio

Peça ao responsável o link do relatório. Você acessa direto pelo navegador sem precisar rodar nada no Python.
