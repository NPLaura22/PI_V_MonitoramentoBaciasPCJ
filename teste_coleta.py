from src.collectors.bs4_collector import BS4Collector


coletor = BS4Collector(
    nome_fonte="G1 Campinas e Regiao",
    url_base="https://g1.globo.com/sp/campinas-regiao/"
)

noticias = coletor.coletar()

print(f"Total de possíveis notícias coletadas: {len(noticias)}")
print("-" * 60)

for noticia in noticias[:10]:
    print(f"Título: {noticia['titulo']}")
    print(f"URL: {noticia['url']}")
    print(f"Fonte: {noticia['fonte_nome']}")
    print(f"Coleta: {noticia['data_coleta']}")
    print("-" * 60)