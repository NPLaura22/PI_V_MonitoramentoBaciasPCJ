#!/usr/bin/env python3
"""
demo_pipeline_summary.py

Script de demonstração para apresentação.
Mostra resumo do pipeline em 1 tela sem muito texto.

Uso:
    PYTHONPATH=. python3 demo_pipeline_summary.py
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.config.settings import RAW_DATA_DIR

def main():
    print("\n" + "="*70)
    print("DEMONSTRAÇÃO — Pipeline de Monitoramento PCJ")
    print("="*70)

    # Carregar CSV mais recente
    csvs = sorted(RAW_DATA_DIR.glob("pipeline_bruto_*.csv"), reverse=True)

    if not csvs:
        print("❌ Nenhum dado encontrado. Execute: python -m src.main")
        return

    df = pd.read_csv(csvs[0], sep=";")
    print(f"\n📊 Arquivo: {csvs[0].name}")
    print(f"📈 Total de notícias: {len(df)}\n")

    # Estatísticas gerais
    relevantes = df[df["relevante_pcj"] == True]
    irrelevantes = df[df["relevante_pcj"] == False]

    print("FILTRO DE RELEVÂNCIA PCJ")
    print("-" * 70)
    print(f"  ✓ Relevantes:   {len(relevantes):3d}  ({100*len(relevantes)//len(df):2d}%)")
    print(f"  ✗ Irrelevantes: {len(irrelevantes):3d}  ({100*len(irrelevantes)//len(df):2d}%)")

    # Categorias
    print("\nCATEGORIAS (em relevantes)")
    print("-" * 70)
    if len(relevantes) > 0:
        cats = relevantes["categoria"].value_counts()
        for cat, count in cats.items():
            pct = 100*count//len(relevantes)
            print(f"  • {cat:25s} {count:3d}  ({pct:2d}%)")

    # Risco
    print("\nNÍVEIS DE RISCO (em relevantes)")
    print("-" * 70)
    if len(relevantes) > 0:
        riscos = relevantes["nivel_risco"].value_counts().sort_index(ascending=False)
        risk_names = {5: "CRÍTICO", 4: "ALTO", 3: "MODERADO", 2: "ATENÇÃO", 1: "INFO", 0: "IRRELEVANTE"}
        for risco, count in riscos.items():
            name = risk_names.get(risco, "?")
            pct = 100*count//len(relevantes)
            print(f"  • [{risco}] {name:12s} {count:3d}  ({pct:2d}%)")

    # Últimas 5 relevantes
    print("\nÚLTIMAS NOTÍCIAS RELEVANTES")
    print("-" * 70)
    if len(relevantes) > 0:
        ultimas = relevantes[["titulo", "categoria", "nivel_risco"]].head(5)
        for idx, (_, row) in enumerate(ultimas.iterrows(), 1):
            titulo = row["titulo"][:60]
            cat = row["categoria"][:15]
            risk = row["nivel_risco"]
            print(f"  {idx}. [{risk}] {cat:15s} {titulo}...")

    print("\n" + "="*70)
    print("✅ Demonstração concluída!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
