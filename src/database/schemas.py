from google.cloud import bigquery


OCORRENCIAS_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("titulo", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("fonte_nome", "STRING"),
    bigquery.SchemaField("fonte_url", "STRING"),
    bigquery.SchemaField("data_coleta", "TIMESTAMP"),

    bigquery.SchemaField("titulo_extraido", "STRING"),
    bigquery.SchemaField("subtitulo", "STRING"),
    bigquery.SchemaField("texto_original", "STRING"),
    bigquery.SchemaField("texto_limpo", "STRING"),
    bigquery.SchemaField("erro_extracao", "STRING"),

    bigquery.SchemaField("relevante_pcj", "BOOLEAN"),
    bigquery.SchemaField("termos_pcj", "STRING"),
    bigquery.SchemaField("termos_hidricos", "STRING"),
    bigquery.SchemaField("termos_exclusao", "STRING"),

    bigquery.SchemaField("categoria", "STRING"),
    bigquery.SchemaField("evento_principal", "STRING"),
    bigquery.SchemaField("nivel_risco", "INTEGER"),
    bigquery.SchemaField("justificativa_risco", "STRING"),
    bigquery.SchemaField("metodo_classificacao", "STRING"),

    bigquery.SchemaField("data_processamento", "TIMESTAMP"),
]