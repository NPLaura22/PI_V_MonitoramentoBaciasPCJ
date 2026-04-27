import re
import unicodedata


TERMOS_GEOGRAFICOS_PCJ = [
    "pcj",
    "bacias pcj",
    "bacia pcj",
    "piracicaba",
    "capivari",
    "jundiai",
    "jundiaí",
    "rio piracicaba",
    "rio capivari",
    "rio jundiai",
    "rio jundiaí",
    "agencia pcj",
    "agência pcj",
    "comites pcj",
    "comitês pcj",
    "campinas",
    "americana",
    "limeira",
    "sumare",
    "sumaré",
    "paulinia",
    "paulínia",
    "atibaia",
    "braganca paulista",
    "bragança paulista",
    "piracaia",
    "indaiatuba",
    "valinhos",
    "vinhedo",
    "holambra",
    "nova odessa",
    "morungaba",
]


TERMOS_HIDRICOS = [
    "chuva",
    "chuvas",
    "temporal",
    "temporais",
    "alagamento",
    "alagamentos",
    "enchente",
    "enchentes",
    "inundacao",
    "inundação",
    "inundacoes",
    "inundações",
    "estiagem",
    "seca",
    "secas",
    "falta de agua",
    "falta de água",
    "abastecimento de agua",
    "abastecimento de água",
    "racionamento",
    "reservatorio",
    "reservatório",
    "represa",
    "vazao",
    "vazão",
    "nivel do rio",
    "nível do rio",
    "transbordamento",
    "rio transbordou",
    "manancial",
    "mananciais",
    "qualidade da agua",
    "qualidade da água",
    "contaminacao",
    "contaminação",
    "poluicao",
    "poluição",
    "esgoto",
    "saneamento",
    "defesa civil",
    "cemaden",
    "alerta de chuva",
    "alerta meteorologico",
    "alerta meteorológico",
    "risco hidrologico",
    "risco hidrológico",
]


TERMOS_EXCLUSAO = [
    "mega-sena",
    "loteria",
    "quina",
    "apostas",
    "futebol",
    "ponte preta",
    "guarani",
    "olimpiada de matematica",
    "olimpíada de matemática",
    "medalhista",
]


def normalizar_texto(texto):
    """
    Normaliza o texto para facilitar a comparação:
    - transforma em minúsculas
    - remove acentos
    - remove espaços duplicados
    """

    if not texto:
        return ""

    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def termo_aparece(texto, termo):
    """
    Verifica se o termo aparece como palavra/frase real,
    evitando falso positivo com pedaços de palavras.

    Exemplo:
    - 'rio' não deve bater com 'sorteio'
    - 'seca' não deve bater com 'consecutiva'
    """

    texto = normalizar_texto(texto)
    termo = normalizar_texto(termo)

    padrao = r"(?<!\w)" + re.escape(termo) + r"(?!\w)"

    return re.search(padrao, texto) is not None


def encontrar_termos(texto, lista_termos):
    """
    Retorna os termos encontrados no texto.
    """

    encontrados = []

    for termo in lista_termos:
        if termo_aparece(texto, termo):
            encontrados.append(termo)

    return encontrados


def calcular_relevancia_pcj(titulo, texto_original=None):
    """
    Calcula se uma notícia é relevante para o projeto PCJ.

    Critério:
    - não pode cair em termos claros de exclusão
    - precisa ter pelo menos um termo geográfico da região PCJ
    - precisa ter pelo menos um termo hídrico/evento ambiental
    """

    partes_texto = [titulo or ""]

    if texto_original:
        partes_texto.append(texto_original)

    texto_completo = " ".join(partes_texto)

    termos_exclusao = encontrar_termos(texto_completo, TERMOS_EXCLUSAO)

    if termos_exclusao:
        return False

    termos_pcj = encontrar_termos(texto_completo, TERMOS_GEOGRAFICOS_PCJ)
    termos_hidricos = encontrar_termos(texto_completo, TERMOS_HIDRICOS)

    if termos_pcj and termos_hidricos:
        return True

    return False


def explicar_relevancia_pcj(titulo, texto_original=None):
    """
    Retorna uma explicação do motivo da notícia ser ou não relevante.
    Isso ajuda muito no debug e futuramente pode virar coluna no BigQuery.
    """

    partes_texto = [titulo or ""]

    if texto_original:
        partes_texto.append(texto_original)

    texto_completo = " ".join(partes_texto)

    termos_exclusao = encontrar_termos(texto_completo, TERMOS_EXCLUSAO)
    termos_pcj = encontrar_termos(texto_completo, TERMOS_GEOGRAFICOS_PCJ)
    termos_hidricos = encontrar_termos(texto_completo, TERMOS_HIDRICOS)

    relevante = False

    if not termos_exclusao and termos_pcj and termos_hidricos:
        relevante = True

    return {
        "relevante": relevante,
        "termos_exclusao": termos_exclusao,
        "termos_pcj": termos_pcj,
        "termos_hidricos": termos_hidricos,
    }