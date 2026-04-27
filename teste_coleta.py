from datetime import datetime

from src.collectors.bs4_collector import BS4Collector
from src.collectors.news_extractor import NewsExtractor
from src.config.settings import RAW_DATA_DIR
from src.processing.relevance_filter import calcular_relevancia_pcj
from src.utils.file_handler import salvar_csv


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

    noticia["relevante_pcj"] = calcular_relevancia_pcj(
        titulo=noticia["titulo"],
        texto_original=noticia["texto_original"]
    )

    print(f"Relevante PCJ: {noticia['relevante_pcj']}")
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