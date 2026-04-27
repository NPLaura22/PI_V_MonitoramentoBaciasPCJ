from pathlib import Path

import pandas as pd


def salvar_csv(dados, caminho_arquivo):
    """
    Salva uma lista de dicionários em um arquivo CSV.

    Parâmetros:
    dados: lista de dicionários
    caminho_arquivo: caminho onde o CSV será salvo
    """

    if not dados:
        print("Nenhum dado para salvar.")
        return

    caminho = Path(caminho_arquivo)

    caminho.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(dados)

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig",
        sep=";"
    )

    print(f"Arquivo salvo com sucesso: {caminho}")