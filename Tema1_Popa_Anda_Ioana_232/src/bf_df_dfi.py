import copy
import time
from src.graf import *

#### algoritm BF

def breadth_first(start, cuvinte, out):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    out.write("#######################################\n")
    out.write("#         Breadth       First         #\n")
    out.write("#######################################\n")
    NodParcurgere.out = out
    gr = Graph(start, cuvinte)
    print("breadth-first")
    c = [NodParcurgere(1, gr.start, None)]

    while len(c) > 0:
        Graph.maxim = max(Graph.maxim, len(c))
        current_time = time.time()
        if (round(current_time - gr.start_time) > gr.timeout):
            out.write("Timeout!\n")
            return
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent.info):
            nodCurent.afisDrum()
            gr.nsol -= 1
            if gr.nsol == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        c.extend(lSuccesori)

"""continua = True
def depth_first(start, cuvinte, out):
    # vom simula o stiva prin relatia de parinte a nodului curent
    out.write("#######################################\n")
    out.write("#         Depth         First         #\n")
    out.write("#######################################\n")
    NodParcurgere.out = out
    gr = Graph(start, cuvinte)
    print("depth-first")
    #c = [NodParcurgere(1, gr.start, None)]
    df(NodParcurgere(1, gr.start, None), gr, out)


def df(nodCurent, gr, out):
    #Graph.maxim = max(Graph.maxim, len(c))
    global continua
    if not continua:
        return
    current_time = time.time()
    if (round(current_time - gr.start_time) > gr.timeout):
        out.write("Timeout!\n")
        return
    if gr.testeaza_scop(nodCurent.info):
        nodCurent.afisDrum()
        gr.nsol -= 1
        if gr.nsol == 0:
            continua = False
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    #c.extend(lSuccesori)
    for sc in lSuccesori:
        print(gr.nsol)
        if gr.nsol != 0:
            df(sc, gr, out)

def dfi(nodCurent, adancime, nrSolutiiCautate):
    print("Stiva actuala: " + "->".join(nodCurent.obtineDrum()))
    input()
    if adancime == 1 and gr.testeaza_scop(nodCurent):
        print("Solutie: ", end="")
        nodCurent.afisDrum()
        print("\n----------------\n")
        input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    if adancime > 1:
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        for sc in lSuccesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(sc, adancime - 1, nrSolutiiCautate)
    return nrSolutiiCautate


def depth_first_iterativ(start, cuvinte, out):
    out.write("#######################################\n")
    out.write("#      Depth    First   Iterativ      #\n")
    out.write("#######################################\n")
    NodParcurgere.out = out
    gr = Graph(start, cuvinte)
    print("depth-first-iterativ")
    # c = [NodParcurgere(1, gr.start, None)]
    dfi(NodParcurgere(1, gr.start, None), gr, out)
    for i in range(1, gr.nrNoduri + 1):
        if nrSolutiiCautate == 0:
            return
        print("**************\nAdancime maxima: ", i)
        nrSolutiiCautate = dfi(NodParcurgere(gr.noduri.index(gr.start), gr.start, None), i, nrSolutiiCautate)"""


