from typing import List

from disco import Disco
from job import Job

# Cada objeto da classe abaico é uma UCB

class Dispositivo:

    def __init__(self, id, tipo: str):          

        self.em_uso = False             # estado (este em uso ou nao)
        self.tipo = tipo                # tipo (dedicado ou compartilhado)      
        self.id = id                    # identificacao do dispositivo
        self.jobs: List[Job] = []       # lista de jobs ao qual o disp. esta alocado

    def remove_job(self, job_id):

        for idx, job in enumerate(self.jobs):
            if job.id == job_id:
                self.jobs.remove(job)

# Classe para guardar o conjunto de UCB's  

class UCB:

    def __init__(self):
        
        self.dispositivos : List[Dispositivo] = []
        

        teclado = Dispositivo(id = 'teclado', tipo = 'dedicado')
        monitor = Dispositivo(id = 'monitor', tipo = 'dedicado')
        disco = Dispositivo(id = 'disco', tipo = 'compartilhado')
        impressora = Dispositivo(id = 'impressora', tipo = 'dedicado')

        self.dispositivos.append(teclado)
        self.dispositivos.append(monitor)
        self.dispositivos.append(disco)
        self.dispositivos.append(impressora)