"""
risk_classifier.py

Classificador de risco 100% por embeddings semânticos.
Sem regras determinísticas, sem listas de palavras-chave.

Delega toda a lógica para embedding_classifier.py.
"""

from src.nlp.embedding_classifier import (
    classificar_categoria,
    classificar_nivel_risco,
)

EVENTOS = {
    "enchente_alagamento": "enchente/alagamento",
    "estiagem_seca": "estiagem/seca",
    "contaminacao_poluicao": "contaminação/poluição",
    "abastecimento": "problema de abastecimento",
    "alerta_defesa_civil": "alerta de risco",
    "monitoramento_hidrico": "monitoramento hídrico",
    "irrelevante": "nenhum evento hídrico identificado",
}


def analisar_risco(texto: str, relevante_pcj: bool) -> dict:
    """
    Classifica categoria, evento principal, nível de risco e justificativa
    usando apenas embeddings semânticos.

    Compatível com a interface esperada pelo pipeline (main.py):
        categoria (str)
        evento_principal (str)
        nivel_risco (int)
        justificativa_risco (str)
        metodo_classificacao (str)
    """

    # Classificação de categoria
    resultado_categoria = classificar_categoria(texto)
    categoria = resultado_categoria["categoria"]
    confianca_categoria = resultado_categoria["confianca"]

    # Evento principal derivado da categoria
    evento_principal = EVENTOS.get(categoria, "nenhum evento identificado")

    # Classificação de nível de risco
    resultado_risco = classificar_nivel_risco(texto, relevante_pcj)
    nivel_risco = resultado_risco["nivel_risco"]
    confianca_risco = resultado_risco["confianca"]

    # Justificativa automática
    if not relevante_pcj:
        justificativa = (
            "A notícia não apresenta relação semântica suficiente "
            "com eventos hídricos nas Bacias PCJ."
        )
    else:
        justificativa = (
            f"Classificado por embeddings na categoria '{categoria}' "
            f"(confiança: {confianca_categoria:.2f}), "
            f"com evento principal '{evento_principal}' "
            f"e nível de risco {nivel_risco} "
            f"(confiança: {confianca_risco:.2f})."
        )

    metodo = f"EMBEDDING — categoria: {confianca_categoria:.2f} | risco: {confianca_risco:.2f}"

    return {
        "categoria": categoria,
        "evento_principal": evento_principal,
        "nivel_risco": nivel_risco,
        "justificativa_risco": justificativa,
        "metodo_classificacao": metodo,
    }
