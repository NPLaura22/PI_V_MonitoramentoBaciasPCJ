from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """
    Classe base para todos os coletores do projeto.

    A ideia é que cada fonte tenha seu próprio coletor,
    mas todos sigam o mesmo padrão de retorno.
    """

    def __init__(self, nome_fonte, url_base):
        self.nome_fonte = nome_fonte
        self.url_base = url_base

    @abstractmethod
    def coletar(self):
        """
        Método obrigatório.

        Todo coletor precisa implementar esse método
        e retornar uma lista de notícias.
        """
        pass