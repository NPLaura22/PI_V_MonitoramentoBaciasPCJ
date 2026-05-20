"""
bertopic_analyzer.py

Análise exploratória de tópicos usando BERTopic.
Roda sobre os textos já coletados e limpos pelo pipeline,
descobrindo padrões temáticos sem categorias pré-definidas.

Diferente do embedding_classifier, o BERTopic NÃO classifica
em categorias fixas — ele descobre os tópicos que emergem
naturalmente dos dados.

Uso:
    PYTHONPATH=. python3 src/nlp/bertopic_analyzer.py
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

from src.config.settings import RAW_DATA_DIR, DATA_DIR


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

# Número mínimo de notícias em um cluster para ser considerado um tópico.
# Aumentar = menos tópicos, mais representativos.
# Diminuir = mais tópicos, mais específicos.
MIN_TOPIC_SIZE = 3

# Número máximo de palavras representativas por tópico exibidas no relatório.
TOP_N_WORDS = 10


def carregar_csv_mais_recente():
    """
    Carrega o CSV bruto mais recente gerado pelo pipeline.
    """
    csvs = sorted(RAW_DATA_DIR.glob("pipeline_bruto_*.csv"), reverse=True)

    if not csvs:
        raise FileNotFoundError(
            "Nenhum CSV encontrado em data/raw/. "
            "Rode o pipeline primeiro: PYTHONPATH=. python3 -m src.main"
        )

    caminho = csvs[0]
    print(f"Carregando: {caminho.name}")
    df = pd.read_csv(caminho, sep=";")
    print(f"Total de registros: {len(df)}")
    return df


def preparar_textos(df):
    """
    Prepara os textos para o BERTopic.
    Combina título e texto limpo. Remove registros sem texto.
    """
    df = df.copy()

    df["texto_bertopic"] = (
        df["titulo"].fillna("") + ". " + df["texto_limpo"].fillna("")
    ).str.strip()

    # Remove textos muito curtos
    df = df[df["texto_bertopic"].str.len() > 50].reset_index(drop=True)

    print(f"Textos válidos para análise: {len(df)}")
    return df


def executar_bertopic(textos):
    """
    Executa o BERTopic nos textos.

    Usa o mesmo modelo de embeddings do pipeline principal
    para manter consistência.

    Retorna o modelo treinado e os tópicos de cada documento.
    """
    print("\nCarregando modelo de linguagem...")
    modelo_embeddings = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Vectorizer em português — melhora a qualidade das palavras-chave
    vectorizer = CountVectorizer(
        ngram_range=(1, 2),       # palavras simples e bigrams (ex: "rio piracicaba")
        stop_words=None,          # BERTopic tem stopwords próprias
        min_df=2,                 # palavra precisa aparecer em pelo menos 2 docs
        max_features=5000,
    )

    print("Treinando BERTopic...")
    modelo_bertopic = BERTopic(
        embedding_model=modelo_embeddings,
        vectorizer_model=vectorizer,
        min_topic_size=MIN_TOPIC_SIZE,
        nr_topics="auto",         # número de tópicos definido automaticamente
        calculate_probabilities=True,
        verbose=True,
    )

    topicos, probabilidades = modelo_bertopic.fit_transform(textos)

    return modelo_bertopic, topicos, probabilidades


def gerar_relatorio(modelo_bertopic, df, topicos):
    """
    Gera relatório textual dos tópicos encontrados
    e salva CSV com a classificação de cada notícia.
    """

    info_topicos = modelo_bertopic.get_topic_info()
    total_topicos = len(info_topicos[info_topicos["Topic"] != -1])

    print("\n" + "=" * 60)
    print(f"RESULTADO — {total_topicos} tópicos encontrados")
    print("=" * 60)

    # Tópico -1 = ruído (notícias que não se encaixam em nenhum tópico)
    ruido = info_topicos[info_topicos["Topic"] == -1]["Count"].values
    ruido_count = int(ruido[0]) if len(ruido) > 0 else 0

    print(f"Notícias classificadas em tópicos: {len(df) - ruido_count}")
    print(f"Notícias sem tópico claro (ruído): {ruido_count}")
    print("-" * 60)

    for _, linha in info_topicos.iterrows():
        if linha["Topic"] == -1:
            continue

        topico_id = linha["Topic"]
        contagem = linha["Count"]

        palavras = modelo_bertopic.get_topic(topico_id)
        top_palavras = [p[0] for p in palavras[:TOP_N_WORDS]]

        print(f"\nTópico {topico_id} ({contagem} notícias)")
        print(f"  Palavras-chave: {', '.join(top_palavras)}")

        # Exemplos de notícias nesse tópico
        indices_topico = [i for i, t in enumerate(topicos) if t == topico_id]
        exemplos = df.iloc[indices_topico[:3]]["titulo"].tolist()
        print("  Exemplos:")
        for ex in exemplos:
            print(f"    - {ex[:80]}...")

    print("\n" + "=" * 60)

    # Salvar CSV com tópicos atribuídos
    df_resultado = df[["titulo", "url", "fonte_nome", "relevante_pcj", "categoria"]].copy()
    df_resultado["topico_bertopic"] = topicos
    df_resultado["topico_bertopic_label"] = df_resultado["topico_bertopic"].apply(
        lambda t: f"Tópico {t}" if t != -1 else "Ruído"
    )

    # Adicionar palavras-chave do tópico
    def palavras_do_topico(t):
        if t == -1:
            return ""
        palavras = modelo_bertopic.get_topic(t)
        return ", ".join([p[0] for p in palavras[:5]])

    df_resultado["topico_palavras_chave"] = df_resultado["topico_bertopic"].apply(
        palavras_do_topico
    )

    data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = DATA_DIR / "processed" / f"bertopic_resultado_{data_execucao}.csv"
    df_resultado.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8")
    print(f"Resultado salvo em: {caminho_saida}")

    return df_resultado


def comparar_com_embeddings(df_resultado):
    """
    Compara os tópicos do BERTopic com as categorias
    do embedding_classifier para mostrar convergências e divergências.
    """
    print("\n" + "=" * 60)
    print("COMPARAÇÃO: BERTopic vs Embedding Classifier")
    print("=" * 60)

    relevantes = df_resultado[df_resultado["relevante_pcj"] == True]

    if len(relevantes) == 0:
        print("Nenhuma notícia relevante para comparar.")
        return

    print(f"\nNotícias relevantes para PCJ: {len(relevantes)}")
    print("\nDistribuição por categoria (embedding) vs tópico (BERTopic):\n")

    tabela = relevantes.groupby(
        ["categoria", "topico_bertopic_label"]
    ).size().reset_index(name="contagem")

    tabela = tabela.sort_values("contagem", ascending=False)

    for _, linha in tabela.iterrows():
        print(
            f"  {linha['categoria']:25} → {linha['topico_bertopic_label']:15} "
            f"({linha['contagem']} notícias)"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("BERTopic — Análise Exploratória de Tópicos PCJ")
    print("=" * 60)

    # 1. Carregar dados
    df = carregar_csv_mais_recente()

    # 2. Preparar textos
    df = preparar_textos(df)
    textos = df["texto_bertopic"].tolist()

    if len(textos) < 10:
        print("Poucos textos para análise. Rode o pipeline com mais fontes.")
        exit(1)

    # 3. Executar BERTopic
    modelo_bertopic, topicos, probabilidades = executar_bertopic(textos)

    # 4. Gerar relatório
    df_resultado = gerar_relatorio(modelo_bertopic, df, topicos)

    # 5. Comparar com embedding_classifier
    comparar_com_embeddings(df_resultado)

    print("\nAnálise BERTopic concluída.")
