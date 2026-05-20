"""
views.py

Gera os comandos SQL para criar (ou recriar) as views analíticas
do BigQuery que alimentam o dashboard no Looker/Data Studio.

Uso:
    python teste_bigquery_criar_views.py
"""


def get_views_sql(project_id: str, dataset_id: str, table_ocorrencias: str) -> dict:
    """
    Retorna um dicionário {nome_view: sql} com todas as views do projeto.

    As views são projetadas para o Looker/Data Studio e incluem:
        - vw_ocorrencias_dashboard   → base geral do dashboard (deduplicada)
        - vw_ocorrencias_relevantes  → apenas notícias relevantes para PCJ
        - vw_indicadores_gerais      → cards de KPI
        - vw_risco_por_categoria     → gráfico de barras por categoria
        - vw_risco_por_periodo       → série temporal de ocorrências
        - vw_fontes                  → resumo por fonte
        - vw_confianca_embeddings    → qualidade e rastreabilidade dos embeddings
    """

    tabela = f"`{project_id}.{dataset_id}.{table_ocorrencias}`"

    views = {}

    # ------------------------------------------------------------------
    # vw_ocorrencias_dashboard
    # Base geral do dashboard. Remove duplicatas pelo campo id,
    # mantendo sempre o registro mais recente (maior data_processamento).
    # Inclui campos de confiança dos embeddings para filtros avançados.
    # ------------------------------------------------------------------
    views["vw_ocorrencias_dashboard"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_ocorrencias_dashboard` AS
WITH deduplicado AS (
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

  titulo_extraido,
  subtitulo,
  texto_limpo,
  erro_extracao,

  relevante_pcj,
  confianca_relevante,
  confianca_irrelevante,
  margem_relevancia,
  metodo_relevancia,

  categoria,
  CASE categoria
    WHEN 'enchente_alagamento'   THEN 'Enchente / Alagamento'
    WHEN 'estiagem_seca'         THEN 'Estiagem / Seca'
    WHEN 'contaminacao_poluicao' THEN 'Contaminação / Poluição'
    WHEN 'abastecimento'         THEN 'Abastecimento'
    WHEN 'alerta_defesa_civil'   THEN 'Alerta Defesa Civil'
    WHEN 'monitoramento_hidrico' THEN 'Monitoramento Hídrico'
    WHEN 'irrelevante'           THEN 'Irrelevante'
    ELSE 'Outros'
  END AS categoria_label,

  evento_principal,
  nivel_risco,
  CASE nivel_risco
    WHEN 0 THEN 'Irrelevante'
    WHEN 1 THEN 'Informativo'
    WHEN 2 THEN 'Atenção'
    WHEN 3 THEN 'Moderado'
    WHEN 4 THEN 'Alto'
    WHEN 5 THEN 'Crítico'
    ELSE 'Desconhecido'
  END AS nivel_risco_label,

  justificativa_risco,
  metodo_classificacao,
  data_processamento
FROM deduplicado
WHERE rn = 1
"""

    # ------------------------------------------------------------------
    # vw_ocorrencias_relevantes
    # Apenas notícias com relevante_pcj = TRUE.
    # Usada na Página 2 do dashboard (tabela detalhada + filtros).
    # ------------------------------------------------------------------
    views["vw_ocorrencias_relevantes"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_ocorrencias_relevantes` AS
SELECT
  id,
  titulo,
  url,
  fonte_nome,
  data_coleta,
  categoria,
  CASE categoria
    WHEN 'enchente_alagamento'   THEN 'Enchente / Alagamento'
    WHEN 'estiagem_seca'         THEN 'Estiagem / Seca'
    WHEN 'contaminacao_poluicao' THEN 'Contaminação / Poluição'
    WHEN 'abastecimento'         THEN 'Abastecimento'
    WHEN 'alerta_defesa_civil'   THEN 'Alerta Defesa Civil'
    WHEN 'monitoramento_hidrico' THEN 'Monitoramento Hídrico'
    ELSE 'Outros'
  END AS categoria_label,
  evento_principal,
  nivel_risco,
  CASE nivel_risco
    WHEN 1 THEN 'Informativo'
    WHEN 2 THEN 'Atenção'
    WHEN 3 THEN 'Moderado'
    WHEN 4 THEN 'Alto'
    WHEN 5 THEN 'Crítico'
    ELSE 'Desconhecido'
  END AS nivel_risco_label,
  justificativa_risco,
  confianca_relevante,
  margem_relevancia,
  data_processamento
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
WHERE relevante_pcj = TRUE
ORDER BY data_coleta DESC
"""

    # ------------------------------------------------------------------
    # vw_indicadores_gerais
    # Agregados para os cards de KPI do dashboard.
    # ------------------------------------------------------------------
    views["vw_indicadores_gerais"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_indicadores_gerais` AS
SELECT
  COUNT(*)                                                        AS total_ocorrencias,
  COUNTIF(relevante_pcj = TRUE)                                   AS total_relevantes_pcj,
  COUNTIF(relevante_pcj = FALSE)                                  AS total_irrelevantes,
  COUNTIF(relevante_pcj = TRUE AND nivel_risco >= 3)              AS total_risco_moderado_ou_maior,
  COUNTIF(relevante_pcj = TRUE AND nivel_risco >= 4)              AS total_risco_alto_ou_critico,
  ROUND(AVG(CASE WHEN relevante_pcj = TRUE THEN nivel_risco END), 2) AS media_nivel_risco,
  MAX(data_coleta)                                                AS ultima_data_coleta,
  COUNT(DISTINCT fonte_nome)                                      AS total_fontes,
  ROUND(AVG(confianca_relevante), 4)                              AS media_confianca_relevante,
  ROUND(AVG(margem_relevancia), 4)                                AS media_margem_relevancia
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
"""

    # ------------------------------------------------------------------
    # vw_risco_por_categoria
    # Agrupamento por categoria para o gráfico de barras.
    # ------------------------------------------------------------------
    views["vw_risco_por_categoria"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_risco_por_categoria` AS
SELECT
  categoria,
  categoria_label,
  COUNT(*)                                       AS total_ocorrencias,
  COUNTIF(relevante_pcj = TRUE)                  AS total_relevantes,
  ROUND(AVG(nivel_risco), 2)                     AS media_risco,
  MAX(nivel_risco)                               AS risco_maximo,
  ROUND(AVG(confianca_relevante), 4)             AS media_confianca,
  COUNTIF(nivel_risco >= 4)                      AS total_alto_critico
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
WHERE relevante_pcj = TRUE
GROUP BY categoria, categoria_label
ORDER BY media_risco DESC
"""

    # ------------------------------------------------------------------
    # vw_risco_por_periodo
    # Série temporal diária para o gráfico de evolução.
    # ------------------------------------------------------------------
    views["vw_risco_por_periodo"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_risco_por_periodo` AS
SELECT
  DATE(data_coleta)                              AS data,
  categoria_label,
  nivel_risco,
  nivel_risco_label,
  COUNT(*)                                       AS total_ocorrencias,
  COUNTIF(relevante_pcj = TRUE)                  AS total_relevantes,
  ROUND(AVG(confianca_relevante), 4)             AS media_confianca_relevante
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
GROUP BY
  DATE(data_coleta),
  categoria_label,
  nivel_risco,
  nivel_risco_label
ORDER BY data DESC, nivel_risco DESC
"""

    # ------------------------------------------------------------------
    # vw_fontes
    # Resumo por fonte para a Página 3 do dashboard.
    # ------------------------------------------------------------------
    views["vw_fontes"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_fontes` AS
SELECT
  fonte_nome,
  fonte_url,
  COUNT(*)                                       AS total_ocorrencias,
  COUNTIF(relevante_pcj = TRUE)                  AS total_relevantes,
  COUNTIF(relevante_pcj = FALSE)                 AS total_irrelevantes,
  ROUND(
    SAFE_DIVIDE(
      COUNTIF(relevante_pcj = TRUE),
      COUNT(*)
    ) * 100, 1
  )                                              AS pct_relevantes,
  ROUND(AVG(CASE WHEN relevante_pcj = TRUE THEN nivel_risco END), 2) AS media_risco_relevantes,
  MAX(data_coleta)                               AS ultima_coleta,
  MIN(data_coleta)                               AS primeira_coleta
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
GROUP BY fonte_nome, fonte_url
ORDER BY total_ocorrencias DESC
"""

    # ------------------------------------------------------------------
    # vw_confianca_embeddings
    # Rastreabilidade e qualidade do modelo de embeddings.
    # Útil para monitorar se o modelo está classificando bem ao longo do tempo.
    # ------------------------------------------------------------------
    views["vw_confianca_embeddings"] = f"""
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_confianca_embeddings` AS
SELECT
  DATE(data_processamento)                       AS data_processamento,
  relevante_pcj,
  COUNT(*)                                       AS total,
  ROUND(AVG(confianca_relevante), 4)             AS media_confianca_relevante,
  ROUND(AVG(confianca_irrelevante), 4)           AS media_confianca_irrelevante,
  ROUND(AVG(margem_relevancia), 4)               AS media_margem,
  ROUND(MIN(confianca_relevante), 4)             AS min_confianca_relevante,
  ROUND(MAX(confianca_relevante), 4)             AS max_confianca_relevante,
  COUNTIF(margem_relevancia < 0.05)              AS classificacoes_incertas,
  metodo_relevancia
FROM `{project_id}.{dataset_id}.vw_ocorrencias_dashboard`
GROUP BY
  DATE(data_processamento),
  relevante_pcj,
  metodo_relevancia
ORDER BY data_processamento DESC
"""

    return views
