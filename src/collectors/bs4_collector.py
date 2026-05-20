from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class BS4Collector(BaseCollector):
    """
    Coletor genérico usando requests + BeautifulSoup.

    Ele acessa uma página, procura links e tenta identificar
    possíveis notícias reais, ignorando vídeos, páginas genéricas,
    links de menu e conteúdos fora do padrão esperado.
    """

    def __init__(self, nome_fonte, url_base):
        super().__init__(nome_fonte, url_base)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    def _link_parece_noticia(self, url):
        """
        Verifica se a URL tem cara de notícia.

        No G1, notícias normalmente terminam com .ghtml.
        Também ignoramos links de vídeo, playlist, globoplay etc.
        """

        url = url.lower()

        termos_bloqueados = [
            "globoplay",
            "playlist",
            "/videos/",
            "video",
            "/futebol/",
            "ge.globo.com",
            "/loterias/",
            "/podcast/",
            "/ao-vivo/",
        ]

        for termo in termos_bloqueados:
            if termo in url:
                return False

        if ".ghtml" not in url:
            return False

        return True

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
            print(f"Erro ao acessar {self.nome_fonte}: {erro}")
            return noticias

        soup = BeautifulSoup(resposta.text, "lxml")

        links = soup.find_all("a")

        for link in links:
            titulo = link.get_text(strip=True)
            href = link.get("href")

            if not titulo or not href:
                continue

            if len(titulo) < 25:
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