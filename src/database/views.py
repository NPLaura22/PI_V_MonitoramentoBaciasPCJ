def get_views_sql(project_id, dataset_id, table_ocorrencias):
    """
    Retorna os comandos SQL para criação das views do dashboard.
    """

    tabela = f"`{project_id}.{dataset_id}.{table_ocorrencias}`"

    views = {}

    views["vw_ocorrencias_dashboard"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_ocorrencias_dashboard` AS
    WITH base AS (
      SELECT
        *,
        ROW_NUMBER() OVER (
          PARTITION BY id
          ORDER BY data_processamento DESC
        ) AS rn
      FROM {tabela}
    )
    SELECT
      id,
      titulo,
      url,
      fonte_nome,
      fonte_url,
      data_coleta,
      data_processamento,
      titulo_extraido,
      subtitulo,
      texto_limpo,
      relevante_pcj,
      termos_pcj,
      termos_hidricos,
      termos_exclusao,
      categoria,
      evento_principal,
      nivel_risco,
      justificativa_risco,
      metodo_classificacao
    FROM base
    WHERE rn = 1;
    """

    views["vw_ocorrencias_relevantes"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_ocorrencias_relevantes` AS
    SELECT
      *
    FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
    WHERE relevante_pcj = TRUE;
    """

    views["vw_indicadores_gerais"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_indicadores_gerais` AS
    SELECT
      COUNT(*) AS total_ocorrencias,
      COUNTIF(relevante_pcj = TRUE) AS total_relevantes_pcj,
      COUNTIF(nivel_risco = 0) AS total_irrelevantes,
      COUNTIF(nivel_risco = 1) AS total_risco_1_informativo,
      COUNTIF(nivel_risco = 2) AS total_risco_2_atencao,
      COUNTIF(nivel_risco = 3) AS total_risco_3_moderado,
      COUNTIF(nivel_risco = 4) AS total_risco_4_alto,
      COUNTIF(nivel_risco = 5) AS total_risco_5_critico,
      COUNTIF(nivel_risco >= 3) AS total_risco_moderado_ou_maior,
      COUNTIF(nivel_risco >= 4) AS total_risco_alto_ou_critico,
      ROUND(AVG(nivel_risco), 2) AS media_nivel_risco,
      MAX(data_coleta) AS ultima_data_coleta,
      MAX(data_processamento) AS ultima_data_processamento,
      COUNT(DISTINCT fonte_nome) AS total_fontes
    FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`;
    """

    views["vw_risco_por_categoria"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_risco_por_categoria` AS
    SELECT
      categoria,
      COUNT(*) AS total_ocorrencias,
      COUNTIF(relevante_pcj = TRUE) AS total_relevantes_pcj,
      ROUND(AVG(nivel_risco), 2) AS media_nivel_risco,
      MAX(nivel_risco) AS maior_nivel_risco
    FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
    GROUP BY categoria
    ORDER BY total_ocorrencias DESC;
    """

    views["vw_risco_por_periodo"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_risco_por_periodo` AS
    SELECT
      DATE(data_coleta) AS data,
      nivel_risco,
      categoria,
      COUNT(*) AS total_ocorrencias
    FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
    GROUP BY data, nivel_risco, categoria
    ORDER BY data DESC, nivel_risco DESC;
    """

    views["vw_fontes"] = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_fontes` AS
    SELECT
      fonte_nome,
      fonte_url,
      COUNT(*) AS total_ocorrencias,
      COUNTIF(relevante_pcj = TRUE) AS total_relevantes_pcj,
      MAX(data_coleta) AS ultima_coleta
    FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
    GROUP BY fonte_nome, fonte_url
    ORDER BY total_ocorrencias DESC;
    """

    return views