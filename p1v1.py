class Job:

    def __init__(self, id : str, chegada : int, memoria : int, cpu : int):
        self.id = id
        self.chegada = chegada
        self.memoria = memoria
        self.cpu = cpu

    def PrintJob(self):
        pass

class Evento:

    def __init__(self, job_id : str, inst: int, tipo: str):
        self.job_id = job_id
        self.inst = inst
        self.tipo = tipo

    def altera_tipo(self, novo_tipo : str):

        self.tipo = novo_tipo

    def altera_inst(self, novo_inst : str):

        self.inst = novo_inst


def MotorEventosSimples (evento: Evento):

    if (evento.tipo == "Chegada"):
        resultado.write("Job: " + evento.job_id + " Tipo: " + evento.tipo +"\n")
        evento.tipo = "Ingresso"
        evento.inst = 0


    elif (evento.tipo == "Ingresso"):
        resultado.write("Job: " + evento.job_id + " Tipo: " + evento.tipo +"\n")
        evento.tipo = "ReqMem"
        evento.inst = 0

    #elif (evento.tipo == "ReqMem"):
    #    evento.inst = 100

    return evento

    # elif (evento.tipo == "ReqProcess"):
    #     pass

    # elif (evento.tipo == "LiberaMem"):
    #     pass

    # elif (evento.tipo == "FimProcess"):
    #     pass

    # elif (evento.tipo == "SaidaSis"):
    #     pass


# Main

resultado = open ("resultado.txt", "w")

JobMix = []

JobMix.append (Job("1",20, 30, 60))
JobMix.append (Job("2",20, 100, 120))
JobMix.append (Job("3",20, 80, 120))
JobMix.append (Job("4",20, 40, 40))

FilaEventos = []
FilaEventos.append (Evento("1",20, "Chegada"))
FilaEventos.append (Evento("2",20, "Chegada"))
FilaEventos.append (Evento("3",220, "Chegada"))
FilaEventos.append (Evento("4",240, "Chegada"))

clock = 0

while (len(FilaEventos) != 0 and clock <= 50):

    #eventos_inst = [evento.inst for evento in FilaEventos]

    resultado.write("clock: "+str(clock)+"\n")

    for evento in FilaEventos:

        execucao_necessaria = evento.inst == clock or evento.inst == 0

        if execucao_necessaria:

            evento = MotorEventosSimples(evento)
    
    resultado.write("Lista de saida: \n")
    
    for evento in FilaEventos:
        resultado.write("   Job: " + evento.job_id + " Tipo: " + evento.tipo +"\n")
    
    clock = clock +1