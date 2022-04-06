
from memoria import Memoria

class Syscall:

    def __init__(self, io_file_name: str, disco):
        self.io_file_name = io_file_name
        self.disco = disco

        disco.salvar(self.io_file_name)

    def save_on_disk(self):
        self.disco.salvar(self.io_file_name)

class ReadIO(Syscall):

    def __init__(self, io_file_name, disco):
        super().__init__(io_file_name, disco)
        
class WriteIO(Syscall):

    def __init__(self, io_file_name, disco):
        super().__init__(io_file_name, disco)

class ReadFile(Syscall):

    def __init__(self, io_file_name, disco):
        super().__init__(io_file_name, disco)
        
class WriteFile(Syscall):

    def __init__(self, io_file_name, disco):
        super().__init__(io_file_name, disco)

class OpenFile(Syscall):

    def __init__(self, io_file_name, disco, memoria: Memoria):
        super().__init__(io_file_name, disco)

        self.memoria = memoria

    def adicionar_na_memoria(self):
        pass
        # self.memoria.
        
class CloseFile(Syscall):

    def __init__(self, io_file_name, disco, memoria: Memoria):
        super().__init__(io_file_name, disco)

        self.memoria = memoria

    def adicionar_na_memoria(self):
        pass
        # self.memoria.