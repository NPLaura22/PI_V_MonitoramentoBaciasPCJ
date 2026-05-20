"""
relevance_filter.py

Filtro de relevância 100% por embeddings semânticos.
Sem listas de palavras-chave, sem regras manuais.
"""

from src.nlp.embedding_classifier import classificar_relevancia


def explicar_relevancia_pcj(titulo: str, texto_original: str = "") -> dict:
    """
    Decide se uma notícia é relevante para as Bacias PCJ usando embeddings.

    Compatível com a interface esperada pelo pipeline (main.py):
        relevante (bool)
        termos_pcj (list)      → vazio, substituído por embeddings
        termos_hidricos (list) → vazio, substituído por embeddings
        termos_exclusao (list) → vazio, substituído por embeddings

    Campos adicionais para rastreabilidade:
        confianca_relevante (float)
        confianca_irrelevante (float)
        margem (float)
        metodo_relevancia (str)
    """
    resultado = classificar_relevancia(
        titulo=titulo,
        texto=texto_original or "",
    )

    return {
        "relevante": resultado["relevante"],
        "termos_pcj": [],
        "termos_hidricos": [],
        "termos_exclusao": [],
        "confianca_relevante": resultado["confianca_relevante"],
        "confianca_irrelevante": resultado["confianca_irrelevante"],
        "margem": resultado["margem"],
        "metodo_relevancia": "EMBEDDING",
    }
