import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

from src.database.schemas import OCORRENCIAS_SCHEMA


load_dotenv()


class BigQueryClient:
    """
    Cliente responsável pela comunicação com o Google BigQuery.
    """

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.dataset_id = os.getenv("BIGQUERY_DATASET")
        self.table_ocorrencias = os.getenv("BIGQUERY_TABLE_OCORRENCIAS")

        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID não definido no .env")

        if not self.dataset_id:
            raise ValueError("BIGQUERY_DATASET não definido no .env")

        if not self.table_ocorrencias:
            raise ValueError("BIGQUERY_TABLE_OCORRENCIAS não definido no .env")

        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.client = bigquery.Client(project=self.project_id)

    def dataset_ref(self):
        return bigquery.DatasetReference(
            self.project_id,
            self.dataset_id
        )

    def table_ref(self, table_name):
        return self.dataset_ref().table(table_name)

    def criar_dataset_se_nao_existir(self):
        """
        Cria o dataset no BigQuery caso ainda não exista.
        """

        dataset = bigquery.Dataset(self.dataset_ref())
        dataset.location = "US"

        dataset = self.client.create_dataset(
            dataset,
            exists_ok=True
        )

        print(f"Dataset pronto: {dataset.full_dataset_id}")

    def criar_tabela_ocorrencias_se_nao_existir(self):
        """
        Cria a tabela de ocorrências caso ainda não exista.
        """

        table = bigquery.Table(
            self.table_ref(self.table_ocorrencias),
            schema=OCORRENCIAS_SCHEMA
        )

        table = self.client.create_table(
            table,
            exists_ok=True
        )

        print(f"Tabela pronta: {table.full_table_id}")

    def enviar_dataframe(self, df, table_name=None):
        """
        Envia um DataFrame para uma tabela do BigQuery.
        """

        if table_name is None:
            table_name = self.table_ocorrencias

        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        job = self.client.load_table_from_dataframe(
            df,
            table_id,
            job_config=job_config
        )

        job.result()

        print(f"{len(df)} registros enviados para {table_id}")

    def enviar_csv(self, caminho_csv, table_name=None, sep=";"):
        """
        Lê um CSV local e envia para o BigQuery.
        """

        caminho = Path(caminho_csv)

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        df = pd.read_csv(caminho, sep=sep)

        self.enviar_dataframe(df, table_name=table_name)