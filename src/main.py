"""
main.py

Pipeline principal de monitoramento das Bacias PCJ.

Otimizações de desempenho implementadas:
    1. Coleta paralela — todas as fontes são acessadas ao mesmo tempo
    2. Extração paralela — todas as URLs são acessadas simultaneamente
    3. Embeddings em batch — todas as notícias processadas de uma vez pelo modelo
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os

import yaml
from dotenv import load_dotenv

from src.database.bigquery_client import BigQueryClient
from src.collectors.bs4_collector import BS4Collector
from src.collectors.news_extractor import NewsExtractor
from src.config.settings import RAW_DATA_DIR
from src.processing.cleaner import limpar_texto_noticia
from src.nlp.embedding_classifier import (
    carregar_modelo,
    classificar_relevancia_batch,
    classificar_categoria_e_risco_batch,
)
from src.processing.relevance_filter import explicar_relevancia_pcj
from src.nlp.risk_classifier import analisar_risco
from src.utils.file_handler import salvar_csv
from src.processing.occurrence_formatter import padronizar_ocorrencia

load_dotenv()

# Número de threads para coleta e extração paralela
# 10 é um bom equilíbrio — mais threads pode causar bloqueios por rate limit dos sites
MAX_WORKERS_COLETA = 10
MAX_WORKERS_EXTRACAO = 20


def carregar_fontes_ativas():
    caminho_yaml = os.path.join(
        os.path.dirname(__file__),
        "config",
        "fontes.yaml"
    )
    with open(caminho_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    fontes = [f for f in config.get("fontes", []) if f.get("ativa", False)]
    print(f"Fontes ativas carregadas: {len(fontes)}")
    return fontes


def coletar_fonte(fonte):
    """Coleta links de uma única fonte. Chamado em paralelo."""
    try:
        coletor = BS4Collector(
            nome_fonte=fonte["nome"],
            url_base=fonte["url_base"],
            padrao_noticia=fonte.get("padrao_noticia", "path_contains"),
            termos_noticia=fonte.get("termos_noticia", ["/noticias/", "/noticia/"])
        )
        noticias = coletor.coletar()
        print(f"  [{fonte['nome']}] {len(noticias)} notícias encontradas")
        return noticias
    except Exception as e:
        print(f"  [{fonte['nome']}] Erro na coleta: {e}")
        return []
    

def obter_urls_existentes_bq():
    """
    Conecta no BigQuery usando as propriedades do cliente do grupo
    e retorna um conjunto (set) com todas as URLs já armazenadas.
    """
    enviar_para_bigquery = os.getenv("ENVIAR_PARA_BIGQUERY", "false").lower() == "true"
    if not enviar_para_bigquery:
        print("Aviso: Envio para o BigQuery desativado. Ignorando busca de URLs.")
        return set()

    print("\n🔍 Buscando URLs de notícias já cadastradas no BigQuery...")
    try:
        bq = BigQueryClient()
        table_id = f"{bq.project_id}.{bq.dataset_id}.{bq.table_ocorrencias}"
        
        query = f"SELECT url FROM {table_id}"
        query_job = bq.client.query(query)
        resultados = query_job.result()
        
        urls_banco = {row.url for row in resultados if row.url}
        print(f" Sucesso: Encontradas {len(urls_banco)} URLs exclusivas no BigQuery.")
        return urls_banco

    except Exception as e:
        print(f" Nota: Não foi possível ler o BigQuery ({e}). O robô seguirá sem o filtro.")
        return set()


def extrair_noticia(args):
    """Extrai o conteúdo de uma notícia. Chamado em paralelo."""
    noticia, extrator = args
    try:
        dados = extrator.extrair(noticia["url"])
        noticia["titulo_extraido"] = dados["titulo_extraido"]
        noticia["subtitulo"] = dados["subtitulo"]
        noticia["texto_original"] = dados["texto_original"]
        noticia["erro_extracao"] = dados["erro_extracao"]
        noticia["texto_limpo"] = limpar_texto_noticia(noticia["texto_original"])
        return noticia
    except Exception as e:
        noticia["titulo_extraido"] = None
        noticia["subtitulo"] = None
        noticia["texto_original"] = None
        noticia["erro_extracao"] = str(e)
        noticia["texto_limpo"] = ""
        return noticia


def executar_pipeline():
    inicio = datetime.now()
    fontes = carregar_fontes_ativas()

    # ------------------------------------------------------------------
    # ETAPA 1 — Coleta paralela de todas as fontes ao mesmo tempo
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Coletando notícias de todas as fontes em paralelo...")
    print("=" * 60)

    todas_noticias = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_COLETA) as executor:
        resultados = executor.map(coletar_fonte, fontes)
        for noticias in resultados:
            todas_noticias.extend(noticias)

    print(f"\nTotal coletado: {len(todas_noticias)} notícias de {len(fontes)} fontes")

    # ------------------------------------------------------------------
    # ETAPA 1.5 — Filtro de duplicadas
    # ------------------------------------------------------------------
    urls_existentes = obter_urls_existentes_bq()
    noticias_para_processar = []
    total_puladas = 0

    for noticia in todas_noticias:
        if noticia.get("url") in urls_existentes:
            total_puladas += 1
            continue
        noticias_para_processar.append(noticia)

    # Se não houver nada novo, avisa e pula a extração
    if not noticias_para_processar:
        print("\nTodas as notícias encontradas já estão no BigQuery. Pulando extração.")
        noticias_extraidas = []
    else:
        # ------------------------------------------------------------------
        # ETAPA 2 — Extração paralela do conteúdo de cada URL NOVA
        # ------------------------------------------------------------------
        print(f"\nExtraindo conteúdo de {len(noticias_para_processar)} novas notícias em paralelo...")

        extrator = NewsExtractor()
        args = [(noticia, extrator) for noticia in noticias_para_processar]

        noticias_extraidas = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_EXTRACAO) as executor:
            futures = {executor.submit(extrair_noticia, arg): arg for arg in args}
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    noticia = future.result()
                    noticias_extraidas.append(noticia)
                    if i % 50 == 0:
                        print(f"  Extraídas: {i}/{len(args)}")
                except Exception as e:
                    print(f"  Erro na extração: {e}")

        print(f"Extração concluída: {len(noticias_extraidas)} notícias")

    # ------------------------------------------------------------------
    # ETAPA 3 — Classificação em batch (todas as notícias de uma vez)
    # ------------------------------------------------------------------
    if noticias_extraidas:
        print("\nCarregando modelo de embeddings...")
        carregar_modelo()  # carrega uma vez antes do batch

        print("Classificando relevância em batch...")
        textos_completos = [
            f"{n.get('titulo', '')}. {n.get('texto_limpo', '')}".strip()
            for n in noticias_extraidas
        ]

        resultados_relevancia = classificar_relevancia_batch(textos_completos)

        for noticia, resultado in zip(noticias_extraidas, resultados_relevancia):
            noticia["relevante_pcj"] = resultado["relevante"]
            noticia["confianca_relevante"] = resultado["confianca_relevante"]
            noticia["confianca_irrelevante"] = resultado["confianca_irrelevante"]
            noticia["margem"] = resultado["margem"]
            noticia["metodo_relevancia"] = "EMBEDDING"
            noticia["termos_pcj"] = ""
            noticia["termos_hidricos"] = ""
            noticia["termos_exclusao"] = ""

        relevantes = [n for n in noticias_extraidas if n["relevante_pcj"]]
        print(f"Relevantes PCJ: {len(relevantes)}/{len(noticias_extraidas)}")

        print("Classificando categoria e risco em batch...")
        textos_relevantes = [n.get("texto_limpo", "") for n in relevantes]
        resultados_risco = classificar_categoria_e_risco_batch(textos_relevantes)

        for noticia, resultado in zip(relevantes, resultados_risco):
            noticia["categoria"] = resultado["categoria"]
            noticia["evento_principal"] = resultado["evento_principal"]
            noticia["nivel_risco"] = resultado["nivel_risco"]
            noticia["justificativa_risco"] = resultado["justificativa_risco"]
            noticia["metodo_classificacao"] = resultado["metodo_classificacao"]

        # Notícias irrelevantes recebem valores padrão
        for noticia in noticias_extraidas:
            if not noticia.get("relevante_pcj"):
                noticia.setdefault("categoria", "irrelevante")
                noticia.setdefault("evento_principal", "nenhum evento hídrico identificado")
                noticia.setdefault("nivel_risco", 0)
                noticia.setdefault("justificativa_risco", "Notícia não relevante para as Bacias PCJ.")
                noticia.setdefault("metodo_classificacao", "IRRELEVANTE")

    # ------------------------------------------------------------------
    # ETAPA 4 — Padronização e salvamento
    # ------------------------------------------------------------------
    print("\nPadronizando e salvando resultados...")
    noticias_processadas = []
    for noticia in noticias_extraidas:
        try:
            noticias_processadas.append(padronizar_ocorrencia(noticia))
        except Exception as e:
            print(f"  Erro ao padronizar: {e}")

    noticias_relevantes = [n for n in noticias_processadas if n.get("relevante_pcj")]

    fim = datetime.now()
    duracao = (fim - inicio).seconds

    print("\n" + "=" * 60)
    print(f"Total de fontes processadas:  {len(fontes)}")
    print(f"Total de notícias coletadas:  {len(todas_noticias)}")
    print(f"Total puladas (já no banco):  {total_puladas}")
    print(f"Total processado nesta rodada:{len(noticias_processadas)}")
    print(f"Total relevante para PCJ:     {len(noticias_relevantes)}")
    print(f"Tempo total:                  {duracao}s")
    print("=" * 60)

    # Só salva e envia pro banco se houver dados novos
    if noticias_processadas:
        data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_bruto = RAW_DATA_DIR / f"pipeline_bruto_{data_execucao}.csv"
        caminho_relevante = RAW_DATA_DIR / f"pipeline_relevante_{data_execucao}.csv"

        salvar_csv(noticias_processadas, caminho_bruto)
        salvar_csv(noticias_relevantes, caminho_relevante)

        enviar = os.getenv("ENVIAR_PARA_BIGQUERY", "false").lower() == "true"
        if enviar:
            print("\nEnviando para o BigQuery...")
            try:
                bq = BigQueryClient()
                bq.criar_dataset_se_nao_existir()
                bq.criar_tabela_ocorrencias_se_nao_existir()
                bq.enviar_csv(caminho_bruto)
                print("Envio concluído com sucesso.")
            except Exception as e:
                print(f"Erro ao enviar para BigQuery: {e}")
        else:
            print(f"\nEnvio desativado. Dados salvos em: {caminho_bruto}")
    else:
        print("\nNenhuma notícia nova para salvar no banco nesta rodada.")


if __name__ == "__main__":
    executar_pipeline()