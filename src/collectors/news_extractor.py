import requests
from bs4 import BeautifulSoup


class NewsExtractor:
    """
    Extrai informações internas de uma notícia.

    A função principal dela é acessar a URL da notícia
    e tentar capturar título, subtítulo e corpo do texto.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    def extrair(self, url):
        """
        Acessa a URL da notícia e retorna os dados extraídos.
        """

        dados = {
            "titulo_extraido": None,
            "subtitulo": None,
            "texto_original": None,
            "erro_extracao": None
        }

        try:
            resposta = requests.get(
                url,
                headers=self.headers,
                timeout=20
            )

            resposta.raise_for_status()

        except requests.RequestException as erro:
            dados["erro_extracao"] = str(erro)
            return dados

        soup = BeautifulSoup(resposta.text, "lxml")

        titulo = self._extrair_titulo(soup)
        subtitulo = self._extrair_subtitulo(soup)
        texto = self._extrair_texto(soup)

        dados["titulo_extraido"] = titulo
        dados["subtitulo"] = subtitulo
        dados["texto_original"] = texto

        return dados

    def _extrair_titulo(self, soup):
        """
        Tenta extrair o título principal da notícia.
        """

        h1 = soup.find("h1")

        if h1:
            return h1.get_text(strip=True)

        return None

    def _extrair_subtitulo(self, soup):
        """
        Tenta extrair o subtítulo da notícia.
        """

        subtitulo = soup.find("h2")

        if subtitulo:
            return subtitulo.get_text(strip=True)

        return None

    def _extrair_texto(self, soup):
        """
        Extrai os parágrafos da notícia.

        No G1, boa parte do conteúdo textual fica em tags <p>.
        Por enquanto, vamos capturar todos os parágrafos relevantes.
        """

        paragrafos = soup.find_all("p")

        textos = []

        for p in paragrafos:
            texto = p.get_text(" ", strip=True)

            if not texto:
                continue

            if len(texto) < 40:
                continue

            textos.append(texto)

        if not textos:
            return None

        return "\n".join(textos)