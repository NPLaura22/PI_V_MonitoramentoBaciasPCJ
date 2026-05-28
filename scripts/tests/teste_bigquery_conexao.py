from src.database.bigquery_client import BigQueryClient


bq = BigQueryClient()

bq.criar_dataset_se_nao_existir()
bq.criar_tabela_ocorrencias_se_nao_existir()

print("Conexão com BigQuery validada com sucesso.")