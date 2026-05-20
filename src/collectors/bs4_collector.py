from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class BS4Collector(BaseCollector):
    """
    Coletor genérico usando requests + BeautifulSoup.

    Suporta múltiplos padrões de identificação de notícias:
        - "extension"     : URL termina com extensão específica (ex: .ghtml para G1)
        - "path_contains" : URL contém termos específicos no caminho (ex: /noticias/)

    O padrão e os termos são configurados no fontes.yaml por fonte.
    """

    TERMOS_BLOQUEADOS = [
        "globoplay",
        "playlist",
        "/videos/",
        "/video/",
        "/futebol/",
        "ge.globo.com",
        "/loterias/",
        "/podcast/",
        "/ao-vivo/",
        "/esportes/",
        "/entretenimento/",
        "youtube.com",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "whatsapp.com",
        "/tags/",
        "/categoria/",
        "/author/",
        "/page/",
        "/search/",
        "/busca/",
        "/galeria/",
        "#",
        "javascript:",
        "mailto:",
    ]

    def __init__(
        self,
        nome_fonte,
        url_base,
        padrao_noticia="path_contains",
        termos_noticia=None
    ):
        super().__init__(nome_fonte, url_base)

        self.padrao_noticia = padrao_noticia
        self.termos_noticia = termos_noticia or ["/noticias/", "/noticia/", "/?p="]

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        }

    def _link_parece_noticia(self, url):
        """
        Verifica se a URL tem cara de notícia com base no padrão configurado.
        Rejeita URLs com termos bloqueados independente do padrão.
        """
        url_lower = url.lower()

        # Rejeitar termos bloqueados
        for termo in self.TERMOS_BLOQUEADOS:
            if termo in url_lower:
                return False

        # Garantir que o link é do mesmo domínio ou subdomínio da fonte
        dominio_base = urlparse(self.url_base).netloc
        dominio_link = urlparse(url).netloc

        if dominio_link and dominio_base not in dominio_link and dominio_link not in dominio_base:
            return False

        # Verificar padrão configurado no fontes.yaml
        if self.padrao_noticia == "extension":
            return any(url_lower.endswith(ext) for ext in self.termos_noticia)

        if self.padrao_noticia == "path_contains":
            return any(termo in url_lower for termo in self.termos_noticia)

        return False

    def coletar(self):
        noticias = []
        urls_encontradas = set()

        try:
            resposta = requests.get(
                self.url_base,
                headers=self.headers,
                timeout=20
            )
            resposta.raise_for_status()

        except requests.RequestException as erro:
            print(f"[{self.nome_fonte}] Erro ao acessar: {erro}")
            return noticias

        soup = BeautifulSoup(resposta.text, "lxml")
        links = soup.find_all("a")

        for link in links:
            titulo = link.get_text(strip=True)
            href = link.get("href")

            if not titulo or not href:
                continue

            if len(titulo) < 20:
                continue

            url_completa = urljoin(self.url_base, href)

            if not self._link_parece_noticia(url_completa):
                continue

            if url_completa in urls_encontradas:
                continue

            urls_encontradas.add(url_completa)

            noticia = {
                "titulo": titulo,
                "url": url_completa,
                "fonte_nome": self.nome_fonte,
                "fonte_url": self.url_base,
                "data_coleta": datetime.now().isoformat(timespec="seconds")
            }

            noticias.append(noticia)

        return noticias
