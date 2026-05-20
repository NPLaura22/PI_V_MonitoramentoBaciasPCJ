from pathlib import Path
import yaml

# Caminho raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]

# Caminhos principais
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Arquivo de fontes
FONTES_CONFIG_PATH = BASE_DIR / "src" / "config" / "fontes.yaml"


def carregar_fontes():
    """
    Carrega o arquivo fontes.yaml e retorna a lista de fontes cadastradas.
    """

    with open(FONTES_CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)

    return dados.get("fontes", [])