import os

from dotenv import load_dotenv
from google.cloud import bigquery

from src.database.views import get_views_sql


load_dotenv()


def criar_views():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET")
    table_ocorrencias = os.getenv("BIGQUERY_TABLE_OCORRENCIAS")

    client = bigquery.Client(project=project_id)

    views = get_views_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_ocorrencias=table_ocorrencias
    )

    for nome_view, sql in views.items():
        print(f"Criando ou atualizando view: {nome_view}")

        job = client.query(sql)
        job.result()

        print(f"View pronta: {nome_view}")
        print("-" * 60)


if __name__ == "__main__":
    criar_views()
    print("Todas as views foram criadas com sucesso.")