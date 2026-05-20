from datetime import datetime
import hashlib


def gerar_id_ocorrencia(url, titulo):
    """
    Gera um ID estável para a ocorrência com base na URL e no título.
    """
    base = f"{url or ''}|{titulo or ''}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()


def padronizar_ocorrencia(noticia):
    """
    Garante que a notícia tenha todos os campos esperados
    antes de ser enviada para CSV, BigQuery ou Looker.

    Inclui os campos de rastreabilidade dos embeddings:
        confianca_relevante    — score de similaridade com âncoras "relevante"
        confianca_irrelevante  — score de similaridade com âncoras "irrelevante"
        margem_relevancia      — diferença entre os dois scores acima
        metodo_relevancia      — método usado na classificação de relevância
    """

    agora = datetime.now().isoformat(timespec="seconds")

    return {
        # --- Identificação ---
        "id": gerar_id_ocorrencia(
            noticia.get("url"),
            noticia.get("titulo")
        ),
        "titulo": noticia.get("titulo"),
        "url": noticia.get("url"),
        "fonte_nome": noticia.get("fonte_nome"),
        "fonte_url": noticia.get("fonte_url"),
        "data_coleta": noticia.get("data_coleta"),

        # --- Extração ---
        "titulo_extraido": noticia.get("titulo_extraido"),
        "subtitulo": noticia.get("subtitulo"),
        "texto_original": noticia.get("texto_original"),
        "texto_limpo": noticia.get("texto_limpo"),
        "erro_extracao": noticia.get("erro_extracao"),

        # --- Relevância PCJ ---
        "relevante_pcj": noticia.get("relevante_pcj", False),
        "termos_pcj": noticia.get("termos_pcj"),
        "termos_hidricos": noticia.get("termos_hidricos"),
        "termos_exclusao": noticia.get("termos_exclusao"),

        # --- Rastreabilidade dos embeddings de relevância ---
        "confianca_relevante": noticia.get("confianca_relevante"),
        "confianca_irrelevante": noticia.get("confianca_irrelevante"),
        "margem_relevancia": noticia.get("margem"),
        "metodo_relevancia": noticia.get("metodo_relevancia"),

        # --- Classificação ---
        "categoria": noticia.get("categoria"),
        "evento_principal": noticia.get("evento_principal"),
        "nivel_risco": noticia.get("nivel_risco"),
        "justificativa_risco": noticia.get("justificativa_risco"),
        "metodo_classificacao": noticia.get("metodo_classificacao"),

        # --- Metadados ---
        "data_processamento": agora,
    }
