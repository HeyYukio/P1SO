from arquivo import Arquivo
from disco import Disco, setup_disco
from syscall import ReadIO, WriteIO
from evento import Evento
from job import Job
from typing import List

class Data:
    """
    Classe de armazenamento de dados.
    """

    jobs : List[Job] = []
    eventos : List[Evento] = []
    job_mix : List[Job] = []
    fila_eventos : List[Evento] = []
    vars = {}
    syscalls = {} # job_id: [tipos]
    arquivos : List[Arquivo] = []
    multiprog_level = 1
    virtualization = False


    def __init__(self):
        pass

    def add_disco(self, disco: Disco):
        self.disco = disco

    def add_job(self, job: Job):
        self.jobs.append(job)
        self.syscalls[job.id] = []

    def add_evento(self, evento):
        self.eventos.append(evento)

    def update_job_mix(self, job_mix):
        self.job_mix = job_mix

    def update_fila_eventos(self, fila_eventos):
        self.fila_eventos = fila_eventos

    def set_var(self, var, value):

        self.vars[var] = value

    def increment_var(self, var, value):

        if var in self.vars:
            self.vars[var] += value
        else:
            raise ValueError(f"Variável {var} não declarada")
    
    def add_arquivo(self, arquivo: Arquivo):

        self.arquivos.append(arquivo)

    def get_arquivo_by_name(self, file_name):

        for arquivo in self.arquivos:

            if arquivo.file_name == file_name:
                return arquivo

        raise ValueError(f"Arquivo {file_name} não declarado previamente")

    def add_syscall(self, job_id, syscall):

        self.syscalls[job_id].append(syscall)

    def add_syscalls_to_jobs(self):
        
        for job in self.jobs:
            for syscalls in  self.syscalls[job.id]:
                job.add_syscall(syscalls)

    def export(self):
        processed_data = {}
        self.add_syscalls_to_jobs()

        processed_data['job_mix'] = self.job_mix
        processed_data['jobs'] = self.jobs
        processed_data['vars'] = self.vars
        processed_data['eventos'] = self.eventos
        processed_data['fila_eventos'] = self.fila_eventos
        processed_data['syscalls'] = self.syscalls
        processed_data['arquivos'] = self.arquivos
        processed_data['multiprog_level'] = self.multiprog_level
        processed_data['virtualization'] = self.virtualization

        return processed_data

class Logic:
    """
    Essa classe deve armazenar dados sobre os procedimentos 
    lógicos dos comandos
    """

    def __init__(self):
        pass

class ControlFunc:
    """
    Classe abstrata de funções de controle. Cada keyword deve herdar seus métodos
    """
    max_params = -1

    def __init__(self, command):
        self.command = command
        self.params = command.split()[1:]

        self.check_params()

    def execute_command(self, data: Data, **kwargs):
        pass

    def check_params(self):

        n_params = len(self.params)

        wrong_params = (n_params != self.max_params) and (self.max_params != -1)
        if wrong_params:
            raise ValueError('Parametrização incorreta')

class JOB(ControlFunc):

    max_params = 4

    def __init__(self, command):
        super().__init__(command)

    def execute_command(self, data: Data, **kwargs):
        
        job_id = self.params[0]
        chegada = int(self.params[1])
        memoria = int(self.params[2])
        cpu = int(self.params[3])

        job = Job(id = job_id, chegada = chegada,
                     memoria = memoria, cpu = cpu)

        data.add_job(job)

class JOBMIX(ControlFunc):

    def __init__(self, command):
        super().__init__(command)

    def execute_command(self, data: Data, **kwargs):
        
        JobMix = []
        job_ids = self.params
        
        for job_id in job_ids:
            
            for job in data.jobs:
                if job.id == job_id:
                    JobMix.append(job)
                    break

        JobMix = self.reorder_job_mix(JobMix)
        data.update_job_mix(JobMix)

    @staticmethod
    def reorder_job_mix(JobMix: List[Job]):

        chegadas = [job.chegada for job in JobMix]
        job_mix_argsort = JOBMIX.argsort(chegadas)

        [JobMix[arg] for arg in job_mix_argsort]

        return [JobMix[arg] for arg in job_mix_argsort]

    @staticmethod
    def argsort(seq):
        return [x for x,y in sorted(enumerate(seq), key = lambda x: x[1])]

class SET(ControlFunc):

    max_params = 2

    def execute_command(self, data: Data, **kwargs):

        var_name = self.params[0]
        var_value  = float(self.params[1])

        data.set_var(var_name, var_value)

class INCR(ControlFunc):

    max_params = 2

    def execute_command(self, data: Data, **kwargs):
        var_name = self.params[0]
        var_value  = float(self.params[1])

        data.increment_var(var_name, var_value)
        
class EVENT(ControlFunc):

    def __init__(self, command):
        super().__init__(command)


    def execute_command(self, data: Data, **kwargs):
        n_params = len(self.params)

        if n_params == 1:
            evento = self.event_by_job_id(data)
        else:
            evento = self.complete_event(data)

        data.add_evento(evento)

    def event_by_job_id(self, data: Data):
        job_id = self.params[0]

        has_found_job = False
        for job in data.jobs:
            if job.id == job_id:
                inst = job.chegada
                has_found_job = True

        if not has_found_job:
            raise ValueError(f"Job {job_id} não declarado para a Fila de Eventos")

        return Evento(job_id=job_id, inst=inst, tipo="Chegada")

    def complete_event(self, data: Data):
        job_id = self.params[0]
        inst = self.params[1]
        tipo = self.params[2]

        return Evento(job_id=job_id, inst=inst, tipo=tipo)

class EVENTS(ControlFunc):

    def __init__(self, command):
        super().__init__(command)

    def execute_command(self, data: Data, **kwargs):
        
        fila_eventos = []
        job_ids = self.params
        
        for job_id in job_ids:
            
            for evento in data.eventos:
                if evento.job_id == job_id:
                    fila_eventos.append(evento)
                    break

        fila_eventos = self.reorder_eventos(fila_eventos)
        data.update_fila_eventos(fila_eventos)

    @staticmethod
    def reorder_eventos(fila_eventos: List[Evento]):

        chegadas = [evento.inst for evento in fila_eventos]
        eventos_argsort = EVENTS.argsort(chegadas)

        [fila_eventos[arg] for arg in eventos_argsort]

        return [fila_eventos[arg] for arg in eventos_argsort]

    @staticmethod
    def argsort(seq):
        return [x for x,y in sorted(enumerate(seq), key = lambda x: x[1])]

class SYSCALL(ControlFunc):

    max_params = 3
    available_syscalls = {
        'read_io': ReadIO,
        'write_io': WriteIO
    }

    def __init__(self, command):
        super().__init__(command)

    def execute_command(self, data: Data, **kwargs):

        job_id = self.params[0]
        syscall_type = self.params[1]
        io_file = self.params[2]

        try:
            syscall = self.available_syscalls[syscall_type](io_file, data.disco)
        except ValueError:
            raise ValueError(f"Syscalll {syscall_type} não existente")
    
        data.add_syscall(job_id, syscall)

class COMMENT(ControlFunc):

    def execute_command(self, data: Data, **kwargs):
        pass

class FILE(ControlFunc):

    max_params = 3

    def execute_command(self, data: Data, **kwargs):

        file_name = self.params[0]
        tamanho = int(self.params[1])
        apenas_leitura = bool(self.params[2])

        arquivo = Arquivo(file_name=file_name, tamanho=tamanho, apenas_leitura=apenas_leitura)

        data.add_arquivo(arquivo)

class VIRTULIZATION(ControlFunc):

    max_params = 1

    def execute_command(self, data: Data, **kwargs):
        
        data.virtualization = bool(self.params[0])

class MULTIPROG(ControlFunc):

    max_params = 1

    def execute_command(self, data: Data, **kwargs):
        
        data.multiprog_level = int(self.params[0])

class ControlLanguage:
    """
    Classe de controle de linguagem. Le um txt e executa os seus comandos
    interagindo com a classe ControlFunc (executa o comando) e data (armazenamento)
    """
    keyword_command_map = {
        'JOB': JOB,
        'SYSCALL': SYSCALL,
        'JOBMIX': JOBMIX,
        'SET': SET,
        'INCR': INCR,
        'EVENT': EVENT,
        'EVENTS': EVENTS,
        'FILE': FILE,
        'MULTIPROG': MULTIPROG,
        'VIRTULIZATION': VIRTULIZATION,
        '#': COMMENT
    }

    def __init__(self, file_name: str, disco: Disco):

        self.file_name = file_name
        self.read_file()

        self.data = Data()
        self.data.add_disco(disco)

    def execute_commads(self):
        
        for command in self.commands:
            
            keyword = command.split()[0]

            try:
                control_func = self.keyword_command_map[keyword](command)
            except:
                raise ValueError(f"Comando {keyword} não definido")

            control_func.execute_command(data = self.data)

            print(f"Executed: {command}")

        processed_data = self.data.export()

        return processed_data

    def read_file(self):
        with open(self.file_name, 'r') as f:
            self.commands = f.readlines()

if __name__ == '__main__':
    setup_disco()
    disco = Disco(tamanho = 512)

    control_language = ControlLanguage('jobmix.txt', disco)
    print(control_language.execute_commads())