import copy
import time
from src.graf import *


def a_star_optim(start, cuvinte, out, euristica="banala"):
    out.write("########################################\n")
    out.write("#   A* - open/closed, doar sol min     #\n")
    out.write("########################################\n")
    msg = "Euristica: " + euristica
    spaces = (38 - len(msg)) // 2
    out.write("#" + " " * spaces + msg + " " * (spaces + 1) + "#\n")
    out.write("########################################\n")

    NodParcurgere.out = out
    gr = Graph(start, cuvinte, euristica)
    _astar_optim(gr, out)


def in_list(nod_info, lista):
    for nod in lista:
        if nod_info == nod.info:
            return nod
    return None


def insert(node, lista):
    idx = 0
    while idx < len(lista) - 1 and (node.f > lista[idx].f or (node.f == lista[idx].f and node.g < lista[idx].g)):
        idx += 1
    lista.insert(idx, node)


def _astar_optim(gr, out):
    """Ruleaza A* varianta optimizata pe graful gr si scrie rezultatele in out.
    Args:
        gr (graph): Graful problemei
        out (IO): Fisier iesire.
    """

    print("astar_optim")

    opened = [NodParcurgere(1, gr.start, None)]

    closed = []

    continua = True

    while continua and len(opened) > 0:
        Graph.maxim = max(Graph.maxim, len(opened) + len(closed))
        current_time = time.time()
        if (round(current_time - gr.start_time) > gr.timeout):
            out.write("Timeout!\n")
            return

        current_node = opened.pop(0)
        closed.append(current_node)

        if gr.testeaza_scop(current_node.info):
            current_node.afisDrum()
            continua = False

        succesori = gr.genereazaSuccesori(current_node)
        for nod in succesori:
            info = nod.info
            g = nod.g
            buton = nod.buton
            h = nod.h
            node_open = in_list(info, opened)
            node_parc = NodParcurgere(current_node.id + 1, info, current_node, g, buton, h)
            if node_open is not None:
                if node_open.f > g + h:
                    opened.remove(node_open)
                    insert(node_parc, opened)
                continue
            node_closed = in_list(info, closed)
            if node_closed is not None:
                if node_closed.f > g + h:
                    closed.remove(node_closed)
                    insert(node_parc, opened)
                continue
            insert(node_parc, opened)