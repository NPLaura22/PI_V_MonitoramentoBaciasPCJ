"""
teste_classificacao_amostras.py

Testa a classificação usando notícias simuladas salvas em:
    data/samples/noticias_pcj_simuladas.csv

Gera resultado em:
    data/processed/resultado_classificacao_simulada_*.csv

Uso:
    PYTHONPATH=. python3 teste_classificacao_amostras.py
"""

from datetime import datetime

import pandas as pd

from src.nlp.risk_classifier import analisar_risco
from src.processing.relevance_filter import explicar_relevancia_pcj
from src.config.settings import DATA_DIR
from src.utils.file_handler import salvar_csv


caminho_entrada = DATA_DIR / "samples" / "noticias_pcj_simuladas.csv"
data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
caminho_saida = DATA_DIR / "processed" / f"resultado_classificacao_simulada_{data_execucao}.csv"

df = pd.read_csv(caminho_entrada, sep=";")

resultados = []

for _, linha in df.iterrows():
    titulo = linha["titulo"]
    texto_limpo = linha["texto_limpo"]

    analise_relevancia = explicar_relevancia_pcj(
        titulo=titulo,
        texto_original=texto_limpo
    )

    analise_risco = analisar_risco(
        texto=texto_limpo,
        relevante_pcj=analise_relevancia["relevante"]
    )

    resultado = {
        "titulo": titulo,
        "texto_limpo": texto_limpo,
        "relevante_pcj": analise_relevancia["relevante"],
        "confianca_relevante": analise_relevancia["confianca_relevante"],
        "confianca_irrelevante": analise_relevancia["confianca_irrelevante"],
        "margem_relevancia": analise_relevancia["margem"],
        "metodo_relevancia": analise_relevancia["metodo_relevancia"],
        "termos_pcj": ", ".join(analise_relevancia["termos_pcj"]),
        "termos_hidricos": ", ".join(analise_relevancia["termos_hidricos"]),
        "termos_exclusao": ", ".join(analise_relevancia["termos_exclusao"]),
        "categoria": analise_risco["categoria"],
        "evento_principal": analise_risco["evento_principal"],
        "nivel_risco": analise_risco["nivel_risco"],
        "justificativa_risco": analise_risco["justificativa_risco"],
        "metodo_classificacao": analise_risco["metodo_classificacao"],
    }

    resultados.append(resultado)


print("Resultado da classificação das amostras:")
print("-" * 80)

for item in resultados:
    print(f"Título:             {item['titulo']}")
    print(f"Relevante PCJ:      {item['relevante_pcj']}")
    print(f"Confiança relevante:{item['confianca_relevante']}")
    print(f"Margem:             {item['margem_relevancia']}")
    print(f"Categoria:          {item['categoria']}")
    print(f"Evento principal:   {item['evento_principal']}")
    print(f"Nível de risco:     {item['nivel_risco']}")
    print("-" * 80)

salvar_csv(resultados, caminho_saida)
