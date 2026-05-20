# Como rodar o projeto

## 1. Clonar o repositório

```bash
git clone https://github.com/NPLaura22/PI_V_MonitoramentoBaciasPCJ.git
cd PI_V_MonitoramentoBaciasPCJ
```

## 2. Criar e ativar o ambiente virtual

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

Se der erro de permissão no Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## 4. Configurar o .env

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Abra o `.env` e preencha:
```
GOOGLE_CLOUD_PROJECT_ID=monitoramento-pcj-494612
BIGQUERY_DATASET=pcj_monitoramento
BIGQUERY_TABLE_OCORRENCIAS=ocorrencias
GOOGLE_APPLICATION_CREDENTIALS=/caminho/completo/para/credentials/pcj-bigquery-key.json
ENVIAR_PARA_BIGQUERY=false
```

## 5. Colocar a credencial JSON

Crie a pasta `credentials/` (se não existir) e coloque o arquivo `pcj-bigquery-key.json` dentro.

```
credentials/
  pcj-bigquery-key.json   ← arquivo que você recebeu do responsável do projeto
```

**Importante:** nunca suba esse arquivo para o GitHub.

## 6. Testar o ambiente

```bash
python teste_ambiente.py
python teste_fontes.py
```

## 7. Testar conexão com BigQuery

```bash
PYTHONPATH=. python3 teste_bigquery_conexao.py
```

Resultado esperado:
```
Dataset pronto: monitoramento-pcj-494612:pcj_monitoramento
Tabela pronta: monitoramento-pcj-494612:pcj_monitoramento.ocorrencias
Conexão com BigQuery validada com sucesso.
```

## 8. Rodar o pipeline principal

**Sem enviar para BigQuery (só CSV local):**
```bash
ENVIAR_PARA_BIGQUERY=false
PYTHONPATH=. python3 -m src.main
```

**Enviando para BigQuery:**
```bash
# No .env, mude para: ENVIAR_PARA_BIGQUERY=true
PYTHONPATH=. python3 -m src.main
```

## 9. Enviar dados simulados para o dashboard

```bash
PYTHONPATH=. python3 enviar_amostras_bigquery.py
```

## 10. Criar/atualizar views no BigQuery

```bash
PYTHONPATH=. python3 teste_bigquery_criar_views.py
```

---

## Erros comuns

**`ModuleNotFoundError: No module named 'src'`**
Você rodou `python src/main.py` em vez de `python -m src.main`.
Use sempre: `PYTHONPATH=. python3 -m src.main`

**`No module named 'dotenv'`**
O ambiente virtual não está ativo.
Mac/Linux: `source venv/bin/activate`
Windows: `venv\Scripts\Activate.ps1`

**`GOOGLE_CLOUD_PROJECT_ID não definido`**
O arquivo `.env` não existe ou está com nome errado.
Execute: `cp .env.example .env` e preencha os dados.

**Erro de permissão no BigQuery**
Seu e-mail Google não tem permissão no projeto.
Peça ao responsável para adicionar: BigQuery Data Viewer + BigQuery Job User.
