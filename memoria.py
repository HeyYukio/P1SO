class Particao:
        def __init__(self, job_id : str, addr : int, tamanho : int):
            self.job_id =job_id
            self.tamanho = tamanho
            self.addr = {'start':addr, 'end':addr + tamanho}

class Memoria:

    def __init__(self, tamanho : int):
        
        self.tamanho = tamanho
        self.memoria_disp = tamanho
        self.job_list = []
        self.map_mem = []

    def calcula_memoria_alocada(self):
                
        memoria_alocada = 0
        for evento in self.job_list:
            memoria_alocada += evento.memoria

        return memoria_alocada

    def adiciona_job(self, job):
    
        if self.memoria_disp - job.memoria >= 0:
            self.map_mem.append(Particao(job.id, self.calcula_memoria_alocada(), job.memoria))

            self.job_list.append(job)
            self.memoria_disp = self.memoria_disp - job.memoria
            

            return True
        else:
            print("Não há memória disponível!!!")

            return False

    def remove_job(self, job):
        
        if job in self.job_list:
            self.job_list.remove(job)
            self.memoria_disp = self.memoria_disp + job.memoria
            
            for i, particao in enumerate(self.map_mem):
                if job.id == particao.job_id:
                    self.map_mem.pop(i)

            memoria_atual = 0
            for particao in self.map_mem:
                particao.addr = {'start': memoria_atual, 'end': memoria_atual + particao.tamanho}
                memoria_atual += particao.tamanho + 1

            return True
        else:
            print("Job não está alocado na memória!!!")

            return False

    def adiciona_arquivo(self, file_name : str):
        pass