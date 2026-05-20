"""
enviar_amostras_bigquery.py

Cria notícias simuladas, processa com o pipeline completo (embeddings)
e envia para o BigQuery para enriquecer o dashboard com dados de teste.

Uso:
    PYTHONPATH=. python3 enviar_amostras_bigquery.py
"""

from datetime import datetime
import pandas as pd

from src.config.settings import DATA_DIR
from src.database.bigquery_client import BigQueryClient
from src.nlp.risk_classifier import analisar_risco
from src.processing.relevance_filter import explicar_relevancia_pcj
from src.processing.occurrence_formatter import padronizar_ocorrencia
from src.utils.file_handler import salvar_csv


def montar_noticias_simuladas():
    return [
        {
            "titulo": "Chuva forte causa alagamentos em Campinas",
            "url": "https://exemplo.com/pcj/chuva-forte-campinas",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-20T08:30:00",
            "titulo_extraido": "Chuva forte causa alagamentos em Campinas",
            "subtitulo": "Defesa Civil monitora pontos de risco após temporal.",
            "texto_original": "A Defesa Civil informou que a chuva forte registrada em Campinas causou pontos de alagamento em vias próximas ao Ribeirão Anhumas. Equipes monitoram a situação e orientam moradores a evitar áreas de risco.",
        },
        {
            "titulo": "Baixa vazão preocupa abastecimento em Piracicaba",
            "url": "https://exemplo.com/pcj/baixa-vazao-piracicaba",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-21T09:15:00",
            "titulo_extraido": "Baixa vazão preocupa abastecimento em Piracicaba",
            "subtitulo": "Técnicos acompanham reservatórios e avaliam medidas preventivas.",
            "texto_original": "A redução da vazão do Rio Piracicaba acendeu alerta para o abastecimento de água na região. Técnicos da Agência PCJ acompanham os níveis dos reservatórios e avaliam medidas preventivas para garantir o abastecimento nas Bacias PCJ.",
        },
        {
            "titulo": "CETESB investiga possível contaminação no Rio Jundiaí",
            "url": "https://exemplo.com/pcj/contaminacao-rio-jundiai",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-22T10:20:00",
            "titulo_extraido": "CETESB investiga possível contaminação no Rio Jundiaí",
            "subtitulo": "Moradores relataram odor forte e alteração na coloração da água.",
            "texto_original": "Moradores relataram alteração na coloração da água e odor forte em trecho do Rio Jundiaí. A CETESB foi acionada para investigar possível contaminação e risco ao manancial que integra as Bacias PCJ.",
        },
        {
            "titulo": "Defesa Civil emite alerta para temporais em Atibaia",
            "url": "https://exemplo.com/pcj/alerta-temporais-atibaia",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-23T11:10:00",
            "titulo_extraido": "Defesa Civil emite alerta para temporais em Atibaia",
            "subtitulo": "Previsão indica chuva intensa e risco de alagamentos.",
            "texto_original": "A Defesa Civil emitiu alerta meteorológico para Atibaia e cidades próximas devido à previsão de chuva intensa, rajadas de vento e risco de alagamentos. A região integra as Bacias PCJ e os rios estão sob monitoramento.",
        },
        {
            "titulo": "Agência PCJ divulga relatório sobre qualidade da água",
            "url": "https://exemplo.com/pcj/relatorio-qualidade-agua",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-24T14:00:00",
            "titulo_extraido": "Agência PCJ divulga relatório sobre qualidade da água",
            "subtitulo": "Indicadores permanecem estáveis nas bacias monitoradas.",
            "texto_original": "A Agência PCJ divulgou relatório técnico sobre qualidade da água nas bacias dos rios Piracicaba, Capivari e Jundiaí. O documento aponta estabilidade nos indicadores e não identifica risco imediato ao abastecimento.",
        },
        {
            "titulo": "Reservatório registra queda no nível por estiagem prolongada",
            "url": "https://exemplo.com/pcj/reservatorio-queda-estiagem",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-25T16:40:00",
            "titulo_extraido": "Reservatório registra queda no nível por estiagem prolongada",
            "subtitulo": "Monitoramento indica necessidade de atenção nos próximos dias.",
            "texto_original": "Durante o período de estiagem, técnicos identificaram queda no nível do reservatório que atende municípios da região das Bacias PCJ. A situação ainda não afeta o abastecimento, mas exige monitoramento contínuo.",
        },
        {
            "titulo": "Enchente severa deixa famílias desabrigadas em Americana",
            "url": "https://exemplo.com/pcj/enchente-americana",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-26T07:00:00",
            "titulo_extraido": "Enchente severa deixa famílias desabrigadas em Americana",
            "subtitulo": "Rio Piracicaba transbordou após chuvas intensas.",
            "texto_original": "O Rio Piracicaba transbordou em Americana após chuvas intensas e deixou dezenas de famílias desabrigadas. A Defesa Civil montou abrigo e declarou estado de atenção. O nível do rio ultrapassou a cota de inundação.",
        },
        {
            "titulo": "Racionamento de água começa em Sumaré por escassez hídrica",
            "url": "https://exemplo.com/pcj/racionamento-sumare",
            "fonte_nome": "Fonte Simulada",
            "fonte_url": "https://exemplo.com",
            "data_coleta": "2026-04-27T10:30:00",
            "titulo_extraido": "Racionamento de água começa em Sumaré por escassez hídrica",
            "subtitulo": "Companhia de saneamento implanta rodízio para economizar reservas.",
            "texto_original": "A companhia de saneamento de Sumaré anunciou início de racionamento de água após queda no nível dos reservatórios que abastecem a cidade. O rodízio afeta bairros de forma alternada para garantir o fornecimento mínimo.",
        },
    ]


def processar_noticia_simulada(noticia):
    noticia["texto_limpo"] = noticia["texto_original"]
    noticia["erro_extracao"] = None

    # Relevância via embeddings — captura também confiança e margem
    analise_relevancia = explicar_relevancia_pcj(
        titulo=noticia["titulo"],
        texto_original=noticia["texto_limpo"]
    )

    noticia["relevante_pcj"] = analise_relevancia["relevante"]
    noticia["termos_pcj"] = ", ".join(analise_relevancia["termos_pcj"])
    noticia["termos_hidricos"] = ", ".join(analise_relevancia["termos_hidricos"])
    noticia["termos_exclusao"] = ", ".join(analise_relevancia["termos_exclusao"])

    # Campos de rastreabilidade dos embeddings
    noticia["confianca_relevante"] = analise_relevancia["confianca_relevante"]
    noticia["confianca_irrelevante"] = analise_relevancia["confianca_irrelevante"]
    noticia["margem"] = analise_relevancia["margem"]
    noticia["metodo_relevancia"] = analise_relevancia["metodo_relevancia"]

    # Classificação de categoria e risco via embeddings
    analise_risco = analisar_risco(
        texto=noticia["texto_limpo"],
        relevante_pcj=noticia["relevante_pcj"]
    )

    noticia["categoria"] = analise_risco["categoria"]
    noticia["evento_principal"] = analise_risco["evento_principal"]
    noticia["nivel_risco"] = analise_risco["nivel_risco"]
    noticia["justificativa_risco"] = analise_risco["justificativa_risco"]
    noticia["metodo_classificacao"] = analise_risco["metodo_classificacao"]

    return padronizar_ocorrencia(noticia)


if __name__ == "__main__":
    print("Processando notícias simuladas com embeddings...")
    print("-" * 60)

    noticias = montar_noticias_simuladas()
    noticias_processadas = []

    for noticia in noticias:
        print(f"  Processando: {noticia['titulo']}")
        processada = processar_noticia_simulada(noticia)
        noticias_processadas.append(processada)
        print(f"  Relevante:        {processada['relevante_pcj']}")
        print(f"  Confiança relev.: {processada['confianca_relevante']}")
        print(f"  Margem:           {processada['margem_relevancia']}")
        print(f"  Categoria:        {processada['categoria']}")
        print(f"  Risco:            {processada['nivel_risco']}")
        print("-" * 60)

    data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = DATA_DIR / "processed" / f"amostras_simuladas_bigquery_{data_execucao}.csv"
    salvar_csv(noticias_processadas, caminho_saida)
    print(f"\nCSV salvo em: {caminho_saida}")

    df = pd.DataFrame(noticias_processadas)

    print("\nEnviando para o BigQuery...")
    try:
        bq = BigQueryClient()
        bq.criar_dataset_se_nao_existir()
        bq.criar_tabela_ocorrencias_se_nao_existir()
        bq.enviar_dataframe(df)
        print("Amostras simuladas enviadas para o BigQuery com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar para BigQuery: {e}")
        print("Verifique se o .env está configurado e a chave JSON está no lugar certo.")
