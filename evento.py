from typing import List
from job import Job

class Evento:

    def __init__(self, job_id : str, inst: int, tipo: str):
        self.job_id = job_id
        self.inst = inst
        self.tipo = tipo

    @staticmethod
    def libera_job_do_processador(FilaProcessador: List[Job], job_id: str):

        job_index = None
        for i, job in enumerate(FilaProcessador):
            if job.id == job_id:
                job_index = i

        job_na_memoria = job_index != None
        if job_na_memoria:
            FilaProcessador.pop(job_index)