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

Abra o terminal e rode:

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

Quando funcionar, o terminal vai mostrar `(venv)` no início da linha.

> O ambiente virtual precisa estar ativo sempre que for rodar o projeto. Se fechar o terminal, ative novamente com o comando acima.

---

## Passo 3 — Instalar as dependências

Com o `(venv)` ativo:

```bash
pip install -r requirements.txt
```

Isso vai instalar todas as bibliotecas necessárias, incluindo o modelo de embeddings. Pode demorar alguns minutos na primeira vez.

---

## Passo 4 — Criar o arquivo `.env`

O arquivo `.env` guarda as configurações do projeto. Ele **nunca** vai para o GitHub por segurança, então cada integrante precisa criar o seu.

Copie o arquivo de exemplo:

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
GOOGLE_CLOUD_PROJECT_ID=projeto-integrador-3-457822
BIGQUERY_DATASET=pcj_monitoramento
BIGQUERY_TABLE_OCORRENCIAS=ocorrencias
GOOGLE_APPLICATION_CREDENTIALS=/caminho/completo/para/credentials/pcj-bigquery-key.json
ENVIAR_PARA_BIGQUERY=false
```

> Substitua `/caminho/completo/para/` pelo caminho real no seu computador. Veja o Passo 5 para saber como pegar o arquivo de credencial.

---

## Passo 5 — Colocar a credencial do Google Cloud

O arquivo `pcj-bigquery-key.json` é a chave de acesso ao BigQuery. Ele **não está no GitHub** por segurança.

Peça esse arquivo ao responsável do projeto por um canal seguro (não enviar em grupo público).

Depois de receber:

1. Coloque o arquivo dentro da pasta `credentials/` do projeto
2. Renomeie para `pcj-bigquery-key.json`
3. Atualize o caminho no `.env`

Para saber o caminho exato no seu computador, abra o terminal dentro da pasta do projeto e rode:

```bash
pwd
```

O caminho da credencial será esse resultado + `/credentials/pcj-bigquery-key.json`.

**Exemplo Mac:**
```
GOOGLE_APPLICATION_CREDENTIALS=/Users/seu_usuario/PI_V_MonitoramentoBaciasPCJ/credentials/pcj-bigquery-key.json
```

**Exemplo Windows:**
```
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\seu_usuario\PI_V_MonitoramentoBaciasPCJ\credentials\pcj-bigquery-key.json
```

---

## Passo 6 — Testar o ambiente

Rode em sequência para confirmar que tudo está funcionando:

```bash
PYTHONPATH=. python3 teste_ambiente.py
```
```bash
PYTHONPATH=. python3 teste_fontes.py
```
```bash
PYTHONPATH=. python3 teste_bigquery_conexao.py
```

Resultado esperado do último:
```
Dataset pronto: projeto-integrador-3-457822:pcj_monitoramento
Tabela pronta: projeto-integrador-3-457822:pcj_monitoramento.ocorrencias
Conexão com BigQuery validada com sucesso.
```

---

## Passo 7 — Criar as views no BigQuery

Só precisa rodar uma vez (ou quando o arquivo `src/database/views.py` for alterado):

```bash
PYTHONPATH=. python3 teste_bigquery_criar_views.py
```

Resultado esperado:
```
View pronta: vw_ocorrencias_dashboard
View pronta: vw_ocorrencias_relevantes
View pronta: vw_indicadores_gerais
View pronta: vw_risco_por_categoria
View pronta: vw_risco_por_periodo
View pronta: vw_fontes
View pronta: vw_confianca_embeddings
Todas as views foram criadas com sucesso.
```

---

## Passo 8 — Rodar o pipeline

**Sem enviar para o BigQuery (só salva CSV local):**

Deixe o `.env` com `ENVIAR_PARA_BIGQUERY=false` e rode:

```bash
PYTHONPATH=. python3 -m src.main
```

**Enviando para o BigQuery:**

Mude no `.env`:
```
ENVIAR_PARA_BIGQUERY=true
```

E rode:
```bash
PYTHONPATH=. python3 -m src.main
```

O pipeline vai:
1. Coletar notícias do G1 Campinas automaticamente
2. Extrair o conteúdo de cada notícia
3. Limpar o texto
4. Classificar relevância, categoria e risco por embeddings
5. Salvar CSV em `data/raw/`
6. Enviar para o BigQuery (se habilitado)

Na primeira execução, o modelo de linguagem será baixado automaticamente — isso pode levar 1 a 2 minutos.

---

## Passo 9 — Enviar dados simulados (opcional)

Para popular o dashboard com dados de exemplo para apresentação:

```bash
PYTHONPATH=. python3 enviar_amostras_bigquery.py
```

---

## Comandos úteis

| Comando | O que faz |
|---|---|
| `PYTHONPATH=. python3 -m src.main` | Roda o pipeline completo |
| `PYTHONPATH=. python3 teste_bigquery_conexao.py` | Testa conexão com BigQuery |
| `PYTHONPATH=. python3 teste_bigquery_criar_views.py` | Cria/atualiza as views |
| `PYTHONPATH=. python3 teste_bigquery_envio_csv.py` | Envia o CSV mais recente |
| `PYTHONPATH=. python3 enviar_amostras_bigquery.py` | Envia dados simulados |
| `PYTHONPATH=. python3 teste_coleta.py` | Testa só a coleta |

---

## Erros comuns

**`ModuleNotFoundError: No module named 'dotenv'`**

O ambiente virtual não está ativo. Ative com:
- Mac/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\Activate.ps1`

---

**`ModuleNotFoundError: No module named 'src'`**

Você rodou `python src/main.py` em vez de `python -m src.main`.
Use sempre: `PYTHONPATH=. python3 -m src.main`

---

**`GOOGLE_CLOUD_PROJECT_ID não definido`**

O arquivo `.env` não existe ou tem erro de formatação. Verifique se cada variável está em sua própria linha, sem espaços antes ou depois do `=`.

---

**`File pcj-bigquery-key.json was not found`**

O caminho no `.env` está errado. Rode `pwd` no terminal dentro da pasta do projeto para pegar o caminho correto.

---

**`403 Access Denied`**

Seu email Google não tem permissão no projeto. Peça ao responsável para adicionar no Google Cloud IAM com os papéis: `BigQuery Data Editor` e `BigQuery Job User`.

---

**`externally-managed-environment` ao rodar pip**

O Mac não deixa instalar pacotes fora de um ambiente virtual. Crie e ative o `venv` primeiro (Passo 2) e instale as dependências dentro dele.

---

## Estrutura do projeto

```
PI_V_MonitoramentoBaciasPCJ/
│
├── credentials/          ← coloque aqui o pcj-bigquery-key.json (não vai pro GitHub)
├── data/
│   ├── raw/              ← CSVs gerados pelo pipeline
│   ├── processed/        ← CSVs de amostras processadas
│   └── samples/          ← dados de teste
│
├── src/
│   ├── collectors/       ← coleta de notícias (BS4, NewsExtractor)
│   ├── config/           ← settings.py e fontes.yaml
│   ├── database/         ← BigQuery client, schema e views
│   ├── nlp/              ← embeddings e classificação de risco
│   ├── processing/       ← limpeza, relevância e formatação
│   └── utils/            ← utilitários (salvar CSV)
│
├── .env                  ← suas configurações locais (não vai pro GitHub)
├── .env.example          ← modelo do .env
├── requirements.txt      ← dependências Python
└── src/main.py           ← pipeline principal
```

---

## Dashboard no Looker Studio

O dashboard está disponível para visualização em:
[lookerstudio.google.com](https://lookerstudio.google.com)

Peça ao responsável para compartilhar o link do relatório com seu email Google. Você acessa direto pelo navegador, sem precisar rodar nada no Python.
