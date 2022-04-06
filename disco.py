from typing import List
import os
import shutil

DISCO_PATH = 'disco'

def setup_disco():

    try:
        shutil.rmtree(DISCO_PATH)
    except:
        pass
    
    try:
        os.mkdir(DISCO_PATH)
    except:
        pass

class  Disco:
        def __init__(self, tamanho):
            self.tamanho = tamanho
            self.espaco_utilizado = 0
            self.jobs = []
            self.registers=[]

        def salvar(self, file_name: str):

            try:
                shutil.copy(file_name, DISCO_PATH + '/' + file_name)
            except:
                raise FileExistsError(f'Erro ao salvar {file_name} no disco')

        def adionar_job_no_disco(self, job):
            self.espaco_utilizado += job.memoria
            self.jobs.append(job)

