from datetime import datetime

from src.collectors.bs4_collector import BS4Collector
from src.collectors.news_extractor import NewsExtractor
from src.config.settings import RAW_DATA_DIR
from src.processing.relevance_filter import explicar_relevancia_pcj
from src.utils.file_handler import salvar_csv
from src.processing.cleaner import limpar_texto_noticia
from src.nlp.risk_classifier import analisar_risco


coletor = BS4Collector(
    nome_fonte="G1 Campinas e Regiao",
    url_base="https://g1.globo.com/sp/campinas-regiao/"
)

extrator = NewsExtractor()

noticias = coletor.coletar()

print(f"Total de possíveis notícias coletadas: {len(noticias)}")
print("-" * 60)

for noticia in noticias:
    print(f"Extraindo conteúdo da notícia: {noticia['titulo']}")

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

    print(f"Relevante PCJ: {noticia['relevante_pcj']}")
    print(f"Termos PCJ encontrados: {noticia['termos_pcj']}")
    print(f"Termos hídricos encontrados: {noticia['termos_hidricos']}")
    print(f"Termos de exclusão encontrados: {noticia['termos_exclusao']}")
    print(f"Categoria: {noticia['categoria']}")
    print(f"Evento principal: {noticia['evento_principal']}")
    print(f"Nível de risco: {noticia['nivel_risco']}")
    print("-" * 60)

noticias_relevantes = [
    noticia for noticia in noticias
    if noticia["relevante_pcj"]
]

print(f"Total de possíveis notícias coletadas: {len(noticias)}")
print(f"Total de notícias relevantes para PCJ: {len(noticias_relevantes)}")
print("-" * 60)

print("Resumo das notícias brutas:")
print("-" * 60)

for noticia in noticias:
    print(f"Título: {noticia['titulo']}")
    print(f"URL: {noticia['url']}")
    print(f"Tem texto extraído: {noticia['texto_original'] is not None}")
    print(f"Tem texto limpo: {bool(noticia['texto_limpo'])}")
    print(f"Relevante PCJ: {noticia['relevante_pcj']}")
    print("-" * 60)

if noticias_relevantes:
    print("Notícias relevantes para PCJ:")
    print("-" * 60)

    for noticia in noticias_relevantes:
        print(f"Título: {noticia['titulo']}")
        print(f"URL: {noticia['url']}")
        print(f"Fonte: {noticia['fonte_nome']}")
        print(f"Relevante PCJ: {noticia['relevante_pcj']}")
        print("-" * 60)
else:
    print("Nenhuma notícia relevante para PCJ encontrada nesta coleta.")
    print("-" * 60)

data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")

caminho_saida_bruto = RAW_DATA_DIR / f"coleta_g1_campinas_bruto_{data_execucao}.csv"
caminho_saida_relevante = RAW_DATA_DIR / f"coleta_g1_campinas_relevante_{data_execucao}.csv"

salvar_csv(noticias, caminho_saida_bruto)
salvar_csv(noticias_relevantes, caminho_saida_relevante)