
from typing import List

class Arquivo:

    def __init__(self, file_name: str, tamanho: int, apenas_leitura: bool, acessivel: bool = True):
        self.file_name = file_name
        self.tamanho = tamanho
        self.apenas_leitura = apenas_leitura
        self.jobs = []

class FCB:

    arquivos : List[Arquivo] = []

    def add_arquivo(self, arquivo):

        self.arquivos.append(arquivo)