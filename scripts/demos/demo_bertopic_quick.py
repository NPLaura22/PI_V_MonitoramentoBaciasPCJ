#!/usr/bin/env python3
"""
demo_bertopic_quick.py

Demonstração rápida de BERTopic para apresentação.
Roda em <2 min e mostra tópicos descobertos.

Uso:
    PYTHONPATH=. python3 demo_bertopic_quick.py
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

from src.config.settings import RAW_DATA_DIR, DATA_DIR

MIN_TOPIC_SIZE = 3

def main():
    print("\n" + "="*70)
    print("DEMONSTRAÇÃO — BERTopic: Descoberta Automática de Tópicos")
    print("="*70)

    # 1. Carregar CSV
    csvs = sorted(RAW_DATA_DIR.glob("pipeline_bruto_*.csv"), reverse=True)

    if not csvs:
        print("❌ Nenhum dado encontrado. Execute: python -m src.main")
        return

    df = pd.read_csv(csvs[0], sep=";")
    print(f"\n📂 Carregando: {csvs[0].name}")
    print(f"📊 Total: {len(df)} notícias")

    # 2. Preparar textos
    df_clean = df.copy()
    df_clean["texto"] = (
        df_clean["titulo"].fillna("") + ". " + df_clean["texto_limpo"].fillna("")
    ).str.strip()
    df_clean = df_clean[df_clean["texto"].str.len() > 50].reset_index(drop=True)

    print(f"✓ Textos válidos: {len(df_clean)}")

    if len(df_clean) < 5:
        print("⚠️  Poucas notícias para análise. Precisa de ~20+")
        return

    textos = df_clean["texto"].tolist()

    # 3. Rodar BERTopic (com verbose=False para não poluir output)
    print("\n🧠 Carregando modelo de embeddings...")
    modelo_embeddings = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("🔄 Treinando BERTopic (pode levar 1-2 min)...")
    vectorizer = CountVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)

    modelo_bertopic = BERTopic(
        embedding_model=modelo_embeddings,
        vectorizer_model=vectorizer,
        min_topic_size=MIN_TOPIC_SIZE,
        nr_topics="auto",
        calculate_probabilities=False,
        verbose=False,  # Sem output verboso
    )

    topicos, _ = modelo_bertopic.fit_transform(textos)

    # 4. Resultados
    info_topicos = modelo_bertopic.get_topic_info()
    total_topicos = len(info_topicos[info_topicos["Topic"] != -1])

    print("\n" + "="*70)
    print(f"✅ RESULTADO — {total_topicos} TÓPICOS DESCOBERTOS")
    print("="*70)

    ruido = info_topicos[info_topicos["Topic"] == -1]["Count"].values
    ruido_count = int(ruido[0]) if len(ruido) > 0 else 0

    print(f"\n📈 Notícias em tópicos: {len(df_clean) - ruido_count}")
    print(f"⚠️  Ruído (sem tópico): {ruido_count}")
    print("\n" + "-"*70)

    # Listar tópicos
    for _, linha in info_topicos.iterrows():
        if linha["Topic"] == -1:
            continue

        topico_id = linha["Topic"]
        contagem = linha["Count"]
        palavras = modelo_bertopic.get_topic(topico_id)
        top_palavras = [p[0] for p in palavras[:5]]

        print(f"\n📌 TÓPICO {topico_id} ({contagem} notícias)")
        print(f"   Palavras-chave: {', '.join(top_palavras)}")

        # Exemplos
        indices = [i for i, t in enumerate(topicos) if t == topico_id]
        exemplos = df_clean.iloc[indices[:2]]["titulo"].tolist()
        for ex in exemplos:
            ex_short = (ex[:65] + "...") if len(ex) > 65 else ex
            print(f"   • {ex_short}")

    print("\n" + "="*70)
    print("✅ Análise BERTopic concluída!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
