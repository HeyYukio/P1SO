import syscall as SYSCALL

class Job:

    def __init__(self, id : str, chegada : int, memoria : int, cpu : int):
        
        self.id = id
        self.chegada = chegada
        self.memoria = memoria
        self.cpu = cpu

        self.cpu_restante = cpu
        self.syscalls = []
        self.disp = []
        self.quantum_counter = 0
        self.skip = 0
        self.tem_delay = False        

    def add_syscall(self, syscall):

        self.syscalls.append(syscall)

        if isinstance(syscall, SYSCALL.ReadIO):
            self.disp.append("teclado")
        if isinstance(syscall, SYSCALL.WriteIO):
            self.disp.append("monitor")

    def processa_job(self, cpu_utilizada: int):
        self.cpu_restante = self.cpu_restante - cpu_utilizada 