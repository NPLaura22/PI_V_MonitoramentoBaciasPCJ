import re
import unicodedata


def normalizar_texto(texto):
    """
    Normaliza o texto para facilitar a análise:
    - minúsculas
    - sem acentos
    - espaços padronizados
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


def contem(texto, termos):
    """
    Verifica se algum termo aparece no texto normalizado.
    """

    texto = normalizar_texto(texto)

    for termo in termos:
        termo = normalizar_texto(termo)

        padrao = r"(?<!\w)" + re.escape(termo) + r"(?!\w)"

        if re.search(padrao, texto):
            return True

    return False


def classificar_categoria(texto):
    """
    Classifica a categoria principal da notícia.
    """

    if contem(texto, [
        "enchente",
        "enchentes",
        "alagamento",
        "alagamentos",
        "inundacao",
        "inundacoes",
        "transbordamento",
        "rio transbordou",
    ]):
        return "enchente_alagamento"

    if contem(texto, [
        "estiagem",
        "seca",
        "secas",
        "falta de chuva",
        "baixa vazao",
        "nivel baixo",
        "reservatorio baixo",
    ]):
        return "estiagem_seca"

    if contem(texto, [
        "contaminacao",
        "contaminado",
        "poluicao",
        "esgoto",
        "produto quimico",
        "mancha de oleo",
        "mortandade de peixes",
    ]):
        return "contaminacao_poluicao"

    if contem(texto, [
        "abastecimento",
        "falta de agua",
        "racionamento",
        "interrupcao no fornecimento",
        "rodizio de agua",
    ]):
        return "abastecimento"

    if contem(texto, [
        "defesa civil",
        "cemaden",
        "alerta",
        "alerta meteorologico",
        "alerta de chuva",
        "risco hidrologico",
    ]):
        return "alerta_defesa_civil"

    if contem(texto, [
        "rio",
        "ribeirao",
        "manancial",
        "represa",
        "reservatorio",
        "vazao",
        "qualidade da agua",
    ]):
        return "monitoramento_hidrico"

    return "irrelevante"


def extrair_evento_principal(texto):
    """
    Identifica o evento principal da notícia.
    """

    categoria = classificar_categoria(texto)

    eventos = {
        "enchente_alagamento": "enchente/alagamento",
        "estiagem_seca": "estiagem/seca",
        "contaminacao_poluicao": "contaminação/poluição",
        "abastecimento": "problema de abastecimento",
        "alerta_defesa_civil": "alerta de risco",
        "monitoramento_hidrico": "monitoramento hídrico",
        "irrelevante": "nenhum evento hídrico identificado",
    }

    return eventos.get(categoria, "nenhum evento identificado")


def classificar_nivel_risco(texto, relevante_pcj):
    """
    Classifica o risco de 0 a 5.

    0 = irrelevante
    1 = informativo
    2 = atenção
    3 = moderado
    4 = alto
    5 = crítico
    """

    if not relevante_pcj:
        return 0

    texto_normalizado = normalizar_texto(texto)

    if contem(texto_normalizado, [
        "mortes",
        "desalojados",
        "desabrigados",
        "rompimento de barragem",
        "contaminacao de manancial",
        "interrupcao no abastecimento",
        "estado de calamidade",
    ]):
        return 5

    if contem(texto_normalizado, [
        "transbordamento",
        "familias afetadas",
        "interdicao",
        "enchente",
        "inundacao",
        "alagamento severo",
        "risco alto",
    ]):
        return 4

    if contem(texto_normalizado, [
        "alagamento",
        "chuva forte",
        "temporal",
        "estiagem",
        "baixa vazao",
        "racionamento",
        "alerta",
    ]):
        return 3

    if contem(texto_normalizado, [
        "previsao de chuva",
        "possibilidade de chuva",
        "monitoramento",
        "nivel baixo",
        "reservatorio",
    ]):
        return 2

    return 1


def gerar_justificativa(categoria, evento_principal, nivel_risco, relevante_pcj):
    """
    Gera uma justificativa textual simples.
    """

    if not relevante_pcj:
        return "A notícia não apresenta relação suficiente com eventos hídricos nas Bacias PCJ."

    return (
        f"A notícia foi classificada na categoria '{categoria}', "
        f"com evento principal '{evento_principal}' e nível de risco {nivel_risco}."
    )


def analisar_risco(texto, relevante_pcj):
    """
    Função principal do classificador.
    Retorna categoria, evento, nível de risco e justificativa.
    """

    categoria = classificar_categoria(texto)
    evento_principal = extrair_evento_principal(texto)
    nivel_risco = classificar_nivel_risco(texto, relevante_pcj)

    justificativa = gerar_justificativa(
        categoria=categoria,
        evento_principal=evento_principal,
        nivel_risco=nivel_risco,
        relevante_pcj=relevante_pcj
    )

    return {
        "categoria": categoria,
        "evento_principal": evento_principal,
        "nivel_risco": nivel_risco,
        "justificativa_risco": justificativa,
        "metodo_classificacao": "REGRAS_DETERMINISTICAS",
    }