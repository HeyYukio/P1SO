from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import json
import os
from typing import List
from dispositivo import UCB
from job import Job
from disco import setup_disco, Disco
from evento import Evento
from memoria import Memoria
from job_read import ControlLanguage
from syscall import ReadIO, WriteIO

import random
random.seed(42)

TAMANHO_MEMORIA = 256
TAMANHO_DISCO = 1024
# GRAU_MULTIPROGRAMACAO = 2
TAMANHO_PARTICAO = 100
QUANTUM = 1
# VIRTUALIZADO = False


def sycall_delay(VIRTUALIZADO, job: Job):

    delay_disco = 5
    delay = 0

    for syscall in job.syscalls:

        if isinstance(syscall, ReadIO) or isinstance(syscall, WriteIO):
            if VIRTUALIZADO:
                delay = delay_disco
                delays_txt.write("Delay Disco Job " +
                                 job.id + ": " + str(delay)+"\n")
                print("Delay Disco Job " + job.id + ": " + str(delay))
                job.cpu_restante += delay_disco
            else:
                delay = random.randrange(5, 10)
                delays_txt.write("Delay Usuario Job " +
                                 job.id + ": " + str(delay)+"\n")
                print("Delay Usuario Job " + job.id + ": " + str(delay))
                job.cpu_restante += delay


def encontra_job(job_mix, job_id):

    for job in job_mix:
        if job.id == job_id:
            return job

    return None


def libera_evento(FilaEvento: List[Job], job_id: str):

    job_index = None
    for i, evento in enumerate(FilaEvento):
        if evento.job_id == job_id:
            job_index = i

    return job_index


def processamento_alocado(FilaProcessador: List[Job]):

    processamento_alocado = 0
    if len(FilaProcessador) != 0:
        processamento_alocado = 1

    return processamento_alocado


def MotorEventos(clock: int, fixa_clock: bool, evento: Evento, JobMix: List[Job], memoria: Memoria, FilaProcessador: List[Job], FilaEventos: List[Job], len_adjust: int, disco: Disco):

    delete_job_index = None

    if (evento.tipo == "Chegada"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        evento.tipo = "Ingresso"
        evento.inst = 0
        fixa_clock = 1

    elif (evento.tipo == "Ingresso"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        job = encontra_job(JobMix, evento.job_id)

        disco.adionar_job_no_disco(job)

        if VIRTUALIZADO:

            for syscall in job.syscalls:
                if isinstance(syscall, ReadIO) or isinstance(syscall, WriteIO):
                    syscall.save_on_disk()

                    for dispositivo in ucb.dispositivos:

                        if dispositivo.id == 'disco':
                            dispositivo.jobs.append(job)
                            dispositivo.em_uso = True

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        evento.tipo = "ReqDisp"
        evento.inst = 0
        fixa_clock = 1

    elif (evento.tipo == "ReqDisp"):

        dispositivos_disponiveis = True

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)

        if not VIRTUALIZADO:

            for dispositivo in job.disp:
                for ucb_disp in ucb.dispositivos:
                    if ucb_disp.id == dispositivo:

                        if ucb_disp.em_uso:
                            dispositivos_disponiveis = False

            if dispositivos_disponiveis:

                for dispositivo in job.disp:
                    for ucb_disp in ucb.dispositivos:
                        if ucb_disp.id == dispositivo:
                            if not ucb_disp.em_uso:
                                ucb_disp.em_uso = True

                evento.tipo = "ReqMem"
                evento.inst = 0
                fixa_clock = 1

            else:
                evento.tipo = "ReqDisp"
                evento.inst = 0
        else:
            evento.tipo = "ReqMem"
            evento.inst = 0
            fixa_clock = 1

    elif (evento.tipo == "ReqMem"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)

        memoria_adicionada = memoria.adiciona_job(job)

        if memoria_adicionada:
            evento.tipo = "ReqProcess"
            evento.inst = 0
            fixa_clock = 1
        else:
            evento.tipo = "ReqMem"
            evento.inst = 0

    elif (evento.tipo == "ReqProcess"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)

        processamento_alocado = len(FilaProcessador)

        processamento_disponivel = processamento_alocado < GRAU_MULTIPROGRAMACAO

        if processamento_disponivel:
            FilaProcessador.append(job)
            evento.inst = 0
            evento.tipo = "Executando"
            fixa_clock = 1

        else:
            evento.tipo = "ReqProcess"
            evento.inst = 0

    elif (evento.tipo == "Executando"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")
        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)

        if not job.tem_delay:
            sycall_delay(VIRTUALIZADO, job)
            job.tem_delay = True

        n = len(FilaProcessador)

        if job.cpu_restante <= 0:

            job.processa_job(1)

            evento.tipo = "FimProcess"
            evento.inst = 0
            fixa_clock = 1

        else:

            if (job.cpu_restante - 1/(n+len_adjust) < 0):

                evento.tipo = "FimProcess"
                evento.inst = 0
                fixa_clock = 1
                job.processa_job(1/(n+len_adjust))

            else:

                evento.tipo = "Executando"
                evento.inst = clock + 1
                job.processa_job(1/(n+len_adjust))

    elif (evento.tipo == "FimProcess"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        evento.tipo = "LiberaProcess"

        job = encontra_job(JobMix, evento.job_id)
        Evento.libera_job_do_processador(FilaProcessador, job.id)

        for syscall in job.syscalls:
            if isinstance(syscall, ReadIO) or isinstance(syscall, WriteIO):

                for dispositivo in ucb.dispositivos:

                    if dispositivo.id == 'disco':

                        dispositivo.remove_job(job)

                    if len(dispositivo.jobs) == 0:
                        dispositivo.em_uso = False

        if not VIRTUALIZADO:
            for dispositivo in job.disp:
                for ucb_disp in ucb.dispositivos:
                    if ucb_disp.id == dispositivo:

                        if not ucb_disp.em_uso:
                            ucb_disp.em_uso = False

        evento.inst = 0
        fixa_clock = 1

    elif (evento.tipo == "LiberaProcess"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        evento.inst = 0
        evento.tipo = "LiberaMem"
        fixa_clock = 1

    elif (evento.tipo == "LiberaMem"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")
        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)
        memoria.remove_job(job)

        evento.inst = 0
        evento.tipo = "SaidaSis"

        fixa_clock = 1

    elif (evento.tipo == "SaidaSis"):

        resultado.write("       -Job: " + evento.job_id +
                        "; Tipo: " + evento.tipo + "\n")

        jobs_data.append({"clock": clock,
                          "job_id": evento.job_id,
                          "tipo": evento.tipo,
                          "instante": evento.inst})

        job = encontra_job(JobMix, evento.job_id)
        delete_job_index = libera_evento(FilaEventos, job.id)

        fixa_clock = 1

    return clock, fixa_clock, delete_job_index


# Main
setup_disco()

resultado = open("data/multi/resultado.txt", "w")
delays_txt = open("data/multi/delays.txt", "w")
macro_data = []
jobs_data = []

memoria = Memoria(tamanho=TAMANHO_MEMORIA)
ucb = UCB()
FilaEventos = []

disco = Disco(tamanho=TAMANHO_DISCO)

control_language = ControlLanguage('jobmix.txt', disco)
data = control_language.execute_commads()

JobMix = data['job_mix']
FilaEventos = data['fila_eventos']
arquivos = data['arquivos']
GRAU_MULTIPROGRAMACAO = data['multiprog_level']
VIRTUALIZADO = data['virtualization']

FilaMemoria = []
FilaProcessador = []

clock = 0
ciclos_ociosos = 0

# def listToString(s):

#     # initialize an empty string
#     str1 = ""

#     # traverse in the string
#     for ele in s:
#         str1 += ele

#     # return string
#     return str1

while (len(FilaEventos) != 0 and clock <= 99999):

    resultado.write("\n\nClock: "+str(clock)+"\n")
    resultado.write("\n   Eventos tratados no ciclo: \n\n")

    delete_job_index = None
    fixa_clock = 0

    for evento in FilaEventos:

        len_adjust = 0
        req_counter = 0

        for evento_i in FilaEventos:

            if (evento_i.tipo == "ReqProcess"):
                req_counter = req_counter + 1

        if (req_counter + len(FilaProcessador) <= GRAU_MULTIPROGRAMACAO):
            len_adjust = req_counter
        else:
            len_adjust = GRAU_MULTIPROGRAMACAO - len(FilaProcessador)

        execucao_necessaria = evento.inst == clock or evento.inst == 0

        # print ("clock " + str(clock) +"; len_adjust " +str(len_adjust))

        if execucao_necessaria:

            clock, fixa_clock, delete_job_index = MotorEventos(
                clock, fixa_clock, evento, JobMix, memoria, FilaProcessador, FilaEventos, len_adjust, disco)

            if delete_job_index != None:
                FilaEventos.pop(delete_job_index)

    resultado.write('\n   Jobs em execucao: ' +
                    ', '.join([str(elem.id) for elem in FilaProcessador]))
    resultado.write('\n')

    # resultado.write('\n   Len adjust: ' + str(len_adjust)+"\n")

    resultado.write("\n   Lista de eventos ao fim do ciclo: \n\n")

    for evento in FilaEventos:
        resultado.write("       Job: " + evento.job_id + "; Tipo: " + evento.tipo + "; Inst: " + str(
            evento.inst) + "; cpu restante: "+str((encontra_job(JobMix, evento.job_id)).cpu_restante)+"\n")

    resultado.write(
        f"\n   Memoria: {memoria.calcula_memoria_alocada()}/{TAMANHO_MEMORIA} \n")
    resultado.write(f"\n   Ciclos Ociosos: {ciclos_ociosos} \n")

    macro_data.append({"clock": clock,
                       "memoria": memoria.calcula_memoria_alocada(),
                       "cpu": processamento_alocado(FilaProcessador) > 0,
                       'disco': disco.espaco_utilizado}
                      )

    if (fixa_clock == 0):

        if (len(FilaProcessador) == 0):
            ciclos_ociosos = ciclos_ociosos + 1

        clock = clock + 1


resultado.write(f"\n\nEstatisticas: \n")
resultado.write(f"\n  Ciclos Ociosos: {ciclos_ociosos} \n")

# saving data

folders = ['data', 'data/conti', 'data/multi', 'data/partic']
for folder in folders:
    try:
        os.mkdir(folder)
    except:
        pass

with open('data/multi/multiprog_macro_data.json', 'w') as fp:
    fp.write(
        '[' +
        ',\n'.join(json.dumps(i) for i in macro_data) +
        ']\n')

with open('data/multi/multiprog_jobs_data.json', 'w') as fp:
    fp.write(
        '[' +
        ',\n'.join(json.dumps(i) for i in jobs_data) +
        ']\n')


jobs = pd.read_json('data/multi/multiprog_jobs_data.json')
jobs.set_index('clock', inplace=True)
jobs.tipo.unique()

jobs_ids = sorted(jobs.job_id.unique())
mudancas = pd.DataFrame(index=jobs.tipo.unique())
tempos_fila = []

for job_id in jobs_ids:
    job_id_data = jobs[jobs.job_id == job_id]

    tipo_anterior = ''
    mudancas_de_estado = []
    tempo_espera = 0

    n_rows = job_id_data.shape[0]
    for row in range(n_rows):

        tipo_atual = job_id_data.iloc[row].tipo
        if tipo_atual != tipo_anterior:
            tipo_anterior = tipo_atual
            clock = job_id_data.index[row]

            mudancas_de_estado.append(clock)
        else:
            tempo_espera += 1

    tempos_fila.append(tempo_espera)

    mudancas[f"job={job_id}"] = mudancas_de_estado

intervalo_perma = abs(mudancas - mudancas.shift(-1))

intervalo_perma.loc['TempoEspera'] = tempos_fila
intervalo_perma = intervalo_perma.fillna('-')

print(intervalo_perma)
intervalo_perma.to_csv('data/multi/intervalo_perma.csv')
mudancas.to_csv('data/multi/multiprog_mudancas.csv')


def plot_states_by_job_id(jobs, job_id):

    job_id_data = jobs[jobs.job_id == job_id]

    trace = go.Scatter(x=job_id_data.index,
                       y=job_id_data.tipo,
                       mode='lines+markers',
                       name='job='+str(job_id))

    return trace


fig = make_subplots(specs=[[{"secondary_y": True}]])

for job_id in jobs.job_id.unique():

    fig_trace = plot_states_by_job_id(jobs, job_id)
    fig.add_trace(fig_trace, secondary_y=False)


order = ['Chegada', 'Ingresso', 'ReqDisp', 'ReqMem', 'ReqProcess', 'Executando', 'FimProcess', 'LiberaProcess',
         'LiberaMem', 'SaidaSis', 'Fim']
fig.update_layout(title="Estados dos jobs ao longo do tempo",
                  plot_bgcolor='white', yaxis={'categoryarray': order, 'categoryorder': "array"})

multiprog_on = []
for idx, clock in zip(range(len(jobs.index.unique())), jobs.index.unique()):
    jobs_exec = jobs[(jobs.tipo == "Executando") & (jobs.index == clock)]

    if len(jobs.index.unique()) != idx + 1:
        next_clock = jobs.index.unique()[idx + 1]
    else:
        continue

    if jobs_exec.shape[0] <= 1:
        multiprog_on.append('Execução única')

        if next_clock - clock  > 1:
            for clk in range(clock, next_clock):
                multiprog_on.append('Execução única')

    else:
        multiprog_on.append('Execução multipla')
        last_state = 'Execução multipla'

        if next_clock - clock  > 1:
            for clk in range(clock, next_clock):
                multiprog_on.append('Execução única')

is_multiprog = pd.DataFrame(
    multiprog_on, index=range(jobs.index.unique()[0], jobs.index.unique()[-1]+1), columns=['is_multiprog'])

# # fig = go.Figure()

trace = go.Scatter(x=is_multiprog.index,
                   y=is_multiprog.is_multiprog,
                   fill='tozeroy',
                   line_color='lightgray',
                   name='Execução Multipla')
fig.update_layout(yaxis2={'categoryarray': [
                  'Execução única', 'Execução multipla'], 'categoryorder': "array"})

fig.add_trace(trace, secondary_y=True)

fig.update_xaxes(title="Clock", dtick=100)
fig.update_yaxes(title="Estado Atual")

fig.write_image('data/multi/1multiprog_estados.png')

simulation = pd.read_json('data/multi/multiprog_macro_data.json')
simulation.set_index('clock', inplace=True)

fig = go.Figure()

trace = go.Scatter(x=simulation.index,
                   y=simulation.cpu.apply(lambda proc: 'Ativo' if proc else 'Inativo'))
fig.add_trace(trace)
fig.update_xaxes(range=[0, simulation.index[-1] + 2])

fig.update_xaxes(title="Clock")
fig.update_yaxes(title="Processador",  dtick=20)

fig.update_layout(title="Utilização do processador ao longo do tempo",
                  plot_bgcolor='white', yaxis={'categoryarray': ['Inativo', 'Ativo'], 'categoryorder': "array"})
fig.write_image('data/multi/2multiprog_proc.png')

fig = go.Figure()

trace = go.Scatter(x=simulation.index,
                   y=simulation.memoria * 1000)
fig.add_trace(trace)
fig.update_xaxes(range=[0, simulation.index[-1] + 2])

fig.update_xaxes(title="Clock")
fig.update_yaxes(title="Memória", dtick=10000)

fig.update_layout(title="Utilização da memória ao longo do tempo")
fig.write_image('data/multi/3memoria_multiprog.png')

fig = go.Figure()

trace = go.Scatter(x=simulation.index,
                   y=simulation.disco)
fig.add_trace(trace)
fig.update_xaxes(range=[0, simulation.index[-1] + 2])

fig.update_xaxes(title="Clock")
fig.update_yaxes(title="Disco")

fig.update_layout(title="Armazenamento dos Jobs e Arquivos no disco ao longo do tempo")
fig.write_image('data/multi/4disco_multiprog.png')
