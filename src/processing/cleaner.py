import re


MARCADORES_PARADA = [
    "Veja mais notícias sobre a região",
    "Veja mais notícias sobre a região no g1",
    "Veja mais notícias sobre a região na página do g1",
    "De segunda a sábado, as notícias que você não pode perder",
    "Para se inscrever, entre ou crie uma conta Globo gratuita",
]


def remover_rodape_g1(texto):
    """
    Remove partes finais comuns do G1 que não fazem parte da notícia principal.
    """

    if not texto:
        return ""

    texto_limpo = texto

    for marcador in MARCADORES_PARADA:
        posicao = texto_limpo.find(marcador)

        if posicao != -1:
            texto_limpo = texto_limpo[:posicao]
            break

    return texto_limpo.strip()


def remover_linhas_indesejadas(texto):
    """
    Remove linhas muito curtas ou linhas típicas de legenda/autoria repetida.
    """

    if not texto:
        return ""

    linhas = texto.splitlines()
    linhas_limpas = []

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            continue

        if linha.startswith("Por ") and "g1" in linha:
            continue

        if "— Foto:" in linha:
            continue

        if "Foto:" in linha:
            continue

        if len(linha) < 30:
            continue

        linhas_limpas.append(linha)

    return "\n".join(linhas_limpas)


def remover_espacos_extras(texto):
    """
    Padroniza espaços e quebras de linha.
    """

    if not texto:
        return ""

    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def limpar_texto_noticia(texto):
    """
    Executa a limpeza completa do texto da notícia.
    """

    texto = remover_rodape_g1(texto)
    texto = remover_linhas_indesejadas(texto)
    texto = remover_espacos_extras(texto)

    return texto