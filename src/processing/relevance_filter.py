TERMOS_PCJ = [
    "pcj",
    "bacias pcj",
    "bacia pcj",
    "piracicaba",
    "capivari",
    "jundiaí",
    "jundiai",
    "rio piracicaba",
    "rio capivari",
    "rio jundiaí",
    "rio jundiai",
    "agência pcj",
    "agencia pcj",
    "comitês pcj",
    "comites pcj",
    "campinas",
    "americana",
    "limeira",
    "sumaré",
    "sumare",
    "paulínia",
    "paulinia",
    "atibaia",
    "bragança paulista",
    "braganca paulista",
    "piracaia",
    "indaiatuba",
    "jundiaí",
    "jundiai",
    "capivari",
    "itupeva",
    "vinhedo",
    "valinhos",
    "holambra",
    "nova odessa",
    "santa bárbara d'oeste",
    "santa barbara d'oeste",
]

TERMOS_HIDRICOS = [
    "chuva",
    "temporal",
    "alagamento",
    "enchente",
    "inundação",
    "inundacao",
    "estiagem",
    "seca",
    "falta de água",
    "falta de agua",
    "abastecimento",
    "reservatório",
    "reservatorio",
    "vazão",
    "vazao",
    "rio",
    "ribeirão",
    "ribeirao",
    "manancial",
    "água",
    "agua",
    "contaminação",
    "contaminacao",
    "esgoto",
    "saneamento",
    "defesa civil",
    "alerta",
    "cemaden",
]


def texto_contem_termo(texto, termos):
    """
    Verifica se algum termo da lista aparece no texto.
    """

    texto = texto.lower()

    for termo in termos:
        if termo in texto:
            return True

    return False


def calcular_relevancia_pcj(titulo, texto_original=None):
    """
    Calcula se uma notícia parece relevante para o projeto PCJ.

    Agora analisamos o título e, quando disponível, também o corpo da notícia.
    """

    partes_texto = [titulo or ""]

    if texto_original:
        partes_texto.append(texto_original)

    texto_completo = " ".join(partes_texto).lower()

    tem_termo_pcj = texto_contem_termo(texto_completo, TERMOS_PCJ)
    tem_termo_hidrico = texto_contem_termo(texto_completo, TERMOS_HIDRICOS)

    if tem_termo_pcj and tem_termo_hidrico:
        return True

    return False