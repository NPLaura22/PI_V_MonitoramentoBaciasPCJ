import sys
import pandas as pd
import numpy as np
import requests
import bs4
import feedparser
import yaml
import dateparser

print("Ambiente funcionando!")
print("-" * 40)

print("Versão do Python:")
print(sys.version)

print("-" * 40)
print("Bibliotecas carregadas com sucesso:")

print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")
print(f"Requests: {requests.__version__}")
print(f"BeautifulSoup: {bs4.__version__}")
print(f"Feedparser: {feedparser.__version__}")
print(f"PyYAML: {yaml.__version__}")
print(f"Dateparser: {dateparser.__version__}")

print("-" * 40)
print("Tudo certo até aqui.")