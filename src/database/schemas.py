from google.cloud import bigquery


OCORRENCIAS_SCHEMA = [
    # --- Identificação ---
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("titulo", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("fonte_nome", "STRING"),
    bigquery.SchemaField("fonte_url", "STRING"),
    bigquery.SchemaField("data_coleta", "TIMESTAMP"),

    # --- Extração ---
    bigquery.SchemaField("titulo_extraido", "STRING"),
    bigquery.SchemaField("subtitulo", "STRING"),
    bigquery.SchemaField("texto_original", "STRING"),
    bigquery.SchemaField("texto_limpo", "STRING"),
    bigquery.SchemaField("erro_extracao", "STRING"),

    # --- Relevância PCJ ---
    bigquery.SchemaField("relevante_pcj", "BOOLEAN"),
    bigquery.SchemaField("termos_pcj", "STRING"),
    bigquery.SchemaField("termos_hidricos", "STRING"),
    bigquery.SchemaField("termos_exclusao", "STRING"),

    # --- Campos de rastreabilidade dos embeddings de relevância ---
    # confianca_relevante: score de similaridade com âncoras "relevante" (0.0 a 1.0)
    # confianca_irrelevante: score de similaridade com âncoras "irrelevante" (0.0 a 1.0)
    # margem: diferença entre confianca_relevante e confianca_irrelevante
    # metodo_relevancia: método usado (ex: "EMBEDDING")
    bigquery.SchemaField("confianca_relevante", "FLOAT"),
    bigquery.SchemaField("confianca_irrelevante", "FLOAT"),
    bigquery.SchemaField("margem_relevancia", "FLOAT"),
    bigquery.SchemaField("metodo_relevancia", "STRING"),

    # --- Classificação ---
    bigquery.SchemaField("categoria", "STRING"),
    bigquery.SchemaField("evento_principal", "STRING"),
    bigquery.SchemaField("nivel_risco", "INTEGER"),
    bigquery.SchemaField("justificativa_risco", "STRING"),
    bigquery.SchemaField("metodo_classificacao", "STRING"),

    # --- Metadados ---
    bigquery.SchemaField("data_processamento", "TIMESTAMP"),
]
