from datetime import datetime
import os

from dotenv import load_dotenv
from src.database.bigquery_client import BigQueryClient
from src.collectors.bs4_collector import BS4Collector
from src.collectors.news_extractor import NewsExtractor
from src.config.settings import RAW_DATA_DIR
from src.processing.cleaner import limpar_texto_noticia
from src.processing.relevance_filter import explicar_relevancia_pcj
from src.nlp.risk_classifier import analisar_risco
from src.utils.file_handler import salvar_csv
from src.processing.occurrence_formatter import padronizar_ocorrencia

load_dotenv()

def processar_noticia(noticia, extrator):
    """
    Executa todas as etapas de processamento de uma notícia:
    extração, limpeza, relevância, categoria e risco.
    """

    dados_extraidos = extrator.extrair(noticia["url"])

    noticia["titulo_extraido"] = dados_extraidos["titulo_extraido"]
    noticia["subtitulo"] = dados_extraidos["subtitulo"]
    noticia["texto_original"] = dados_extraidos["texto_original"]
    noticia["erro_extracao"] = dados_extraidos["erro_extracao"]

    noticia["texto_limpo"] = limpar_texto_noticia(
        noticia["texto_original"]
    )

    analise_relevancia = explicar_relevancia_pcj(
        titulo=noticia["titulo"],
        texto_original=noticia["texto_limpo"]
    )

    noticia["relevante_pcj"] = analise_relevancia["relevante"]
    noticia["termos_pcj"] = ", ".join(analise_relevancia["termos_pcj"])
    noticia["termos_hidricos"] = ", ".join(analise_relevancia["termos_hidricos"])
    noticia["termos_exclusao"] = ", ".join(analise_relevancia["termos_exclusao"])

    analise_risco = analisar_risco(
        texto=noticia["texto_limpo"],
        relevante_pcj=noticia["relevante_pcj"]
    )

    noticia["categoria"] = analise_risco["categoria"]
    noticia["evento_principal"] = analise_risco["evento_principal"]
    noticia["nivel_risco"] = analise_risco["nivel_risco"]
    noticia["justificativa_risco"] = analise_risco["justificativa_risco"]
    noticia["metodo_classificacao"] = analise_risco["metodo_classificacao"]

    return noticia


def executar_pipeline():
    """
    Executa o pipeline completo de coleta e processamento.
    """

    coletor = BS4Collector(
        nome_fonte="G1 Campinas e Regiao",
        url_base="https://g1.globo.com/sp/campinas-regiao/"
    )

    extrator = NewsExtractor()

    noticias = coletor.coletar()
    noticias_processadas = []

    print(f"Total de possíveis notícias coletadas: {len(noticias)}")
    print("-" * 60)

    for noticia in noticias:
        print(f"Processando notícia: {noticia['titulo']}")

        noticia_processada = processar_noticia(
            noticia=noticia,
            extrator=extrator
        )

        noticia_padronizada = padronizar_ocorrencia(noticia_processada)

        noticias_processadas.append(noticia_padronizada)

        print(f"Relevante PCJ: {noticia_padronizada['relevante_pcj']}")
        print(f"Categoria: {noticia_padronizada['categoria']}")
        print(f"Nível de risco: {noticia_padronizada['nivel_risco']}")
        print("-" * 60)

    noticias_relevantes = [
        noticia for noticia in noticias_processadas
        if noticia["relevante_pcj"]
    ]

    print(f"Total processado: {len(noticias_processadas)}")
    print(f"Total relevante para PCJ: {len(noticias_relevantes)}")
    print("-" * 60)

    data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_saida_bruto = RAW_DATA_DIR / f"pipeline_bruto_{data_execucao}.csv"
    caminho_saida_relevante = RAW_DATA_DIR / f"pipeline_relevante_{data_execucao}.csv"

    salvar_csv(noticias_processadas, caminho_saida_bruto)
    salvar_csv(noticias_relevantes, caminho_saida_relevante)

    enviar_para_bigquery = os.getenv("ENVIAR_PARA_BIGQUERY", "false").lower() == "true"

    if enviar_para_bigquery:
        print("Enviando dados processados para o BigQuery...")

        bq = BigQueryClient()

        bq.criar_dataset_se_nao_existir()
        bq.criar_tabela_ocorrencias_se_nao_existir()
        bq.enviar_csv(caminho_saida_bruto)

        print("Envio automático para BigQuery concluído.")
    else:
        print("Envio para BigQuery desativado no .env.")

if __name__ == "__main__":
    executar_pipeline()