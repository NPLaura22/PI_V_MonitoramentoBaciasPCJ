from pathlib import Path

from src.database.bigquery_client import BigQueryClient
from src.config.settings import RAW_DATA_DIR


def encontrar_csv_mais_recente():
    """
    Busca o arquivo pipeline_bruto mais recente na pasta data/raw.
    """

    arquivos = list(RAW_DATA_DIR.glob("pipeline_bruto_*.csv"))

    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo pipeline_bruto_*.csv encontrado em data/raw.")

    arquivo_mais_recente = max(arquivos, key=lambda arquivo: arquivo.stat().st_mtime)

    return arquivo_mais_recente


if __name__ == "__main__":
    caminho_csv = encontrar_csv_mais_recente()

    print(f"CSV encontrado: {caminho_csv}")

    bq = BigQueryClient()

    bq.criar_dataset_se_nao_existir()
    bq.criar_tabela_ocorrencias_se_nao_existir()

    bq.enviar_csv(caminho_csv)

    print("Envio para o BigQuery concluído com sucesso.")