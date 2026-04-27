from src.config.settings import carregar_fontes

fontes = carregar_fontes()

print("Fontes cadastradas:")
print("-" * 40)

for fonte in fontes:
    print(f"Nome: {fonte['nome']}")
    print(f"URL: {fonte['url_base']}")
    print(f"Tipo: {fonte['tipo']}")
    print(f"Ativa: {fonte['ativa']}")
    print("-" * 40)