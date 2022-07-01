import sys, getopt, os
from src.bf_df_dfi import *
from src.graf import Graph, NodParcurgere
from src.a_star import a_star
from src.a_star_optim import a_star_optim
from src.ida_star import ida_star


nsol = -1
timeout = -1


def main(argv):
    """ Incarca, parseaza datele de intrare, verifica corectitudinea lor.
    Args:
        argv (list): lista argumentelor din command-line care urmeaza a fi analizate.
                    de obicei coincide cu sys.argv[1:]
        "i:o:n:t:":  șirul de litere de opțiune pe care scriptul dorește să le recunoască
        opts: este o lista de perechi , ex: [(-i, input_folder), ...]
        args: lista de argumente din care se elimina optiunile [<input_folder>, <output_folder>, <nr_solutii>, <timeout>]
        getopt: functie de parsare care are ca argumente lista argumentelor din command-line si șirul de litere de opțiune
        getopt.GetoptError: o opțiune nerecunoscută este găsită în lista de argumente sau când o opțiune care necesită un argument nu este dată
    """
    global nsol, timeout
    input_folder = ''
    output_folder = ''

    try:
        opts, args = getopt.getopt(argv, "i:o:n:t:")
    except getopt.GetoptError:
        print('Eroare! Sintaxa este: main.py -i <input_folder> -o <output_folder> -n <nr_solutii> -t <timeout>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            input_folder = arg
        elif opt == "-o":
            output_folder = arg
        elif opt == "-n":
            nsol = int(arg)
        elif opt == "-t":
            timeout = int(arg)
        else:
            print("Argument error")
            sys.exit(2)

    # daca timeout-ul / nsol nu au fost modificate sau daca directorul respectiv nu exista => eroare
    if timeout == -1 or nsol == -1 or not os.path.isdir(input_folder):
        print("Argument error1")
        sys.exit(2)

    # daca nu exista directorul de output => se creeaza
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # parcurge fisierele din input folder, le deschide pt. citire, iar pentru fiecare fisier si metoda
    # creeaza cate un fisier de output pe care il deschide pentru scriere si al carui nume este
    # "output_" + numele fisierului de input + "_NumeMetoda"

    for filename in os.listdir(input_folder):
        output_filename = "output_" + filename
        inp = open("{0}/{1}".format(input_folder, filename), "r")
        out_bf_df_dfi = open("{0}/{1}_bf_df_dfi".format(output_folder, output_filename), "w")
        out_astar = open("{0}/{1}_astar".format(output_folder, output_filename), "w")
        out_astar_optim = open("{0}/{1}_astar_optim".format(output_folder, output_filename), "w")
        out_idastar = open("{0}/{1}_idastar".format(output_folder, output_filename), "w")

        run(inp, out_bf_df_dfi, out_astar, out_astar_optim, out_idastar)
        inp.close()
        out_bf_df_dfi.close()
        out_astar.close()
        out_astar_optim.close()
        out_idastar.close()


def run(inp, out_bf_df_dfi, out_astar, out_astar_optim, out_idastar):
    """ Pregateste variabilele pentru testul cu datele din fisierul inp. Ruleaza algoritmii.
    Args:
        inp (IO): Fisier input
        out (IO): Fisier output
    """

    """
    Citesc datele din fisierul de intrare
    - citeste linie cu linie pana cand intalneste "__cuvinte__"
    - l = lista cu liniile in care fiecare elem. e un sir
    - mat = lista de liste in care fiecare elem. e un caracter
    - strip = elimina cel mai lung sufix si prefix formate din spatii albe
    - split = furnizeaza o lista formata din caracterele separate din spatiu
    """

    l = []
    linie = inp.readline().strip()
    while linie != "__cuvinte__" and linie != "":
        l.append(linie)
        linie = inp.readline().strip()
    #verificarea corectitudinii datelor de intrare:  sa existe linia "__cuvinte__", dar nu pe primul rand in fisier
    if len(l) == 0:
        print("Input error in fisierul {0}! Fisierul de input nu contine starea initiala. ".format(inp.name))
        sys.exit(-1)
    if linie == "":
        print("Input error in fisierul {0}! Fisierul de input nu contine sirul constant : __cuvinte__. ".format(inp.name))
        sys.exit(-1)
    mat = []
    for linie in l:
        mat.append([x for x in linie.strip().split(' ')])

    # lista cu cuvintele ce trebuie obtinute in matrice
    cuvinte = []
    cuv = inp.readline().strip()
    while cuv:
        cuvinte.append(cuv)
        cuv = inp.readline().strip()

    # verificarea corectitudinii datelor de intrare

    # liniile fisierului pana la linia "__cuvinte__" trebuie sa aiba aceeasi lungime
    lungime_linie = len(l[0])
    for linie in l:
        if len(linie) != lungime_linie:
            print("Input error in fisierul {0}! Linii cu lungime diferita. ".format(inp.name))
            sys.exit(-1)

    # caracterele din input care vor constitui starea initiala trebuie sa fie separate prin spatiu
    for linie in l:
        for i in range(1, len(linie), 2):
            if str(linie[i]) != " ":
                print("Input error in fisierul {0}! Caracterele din input care vor constitui starea initiala nu sunt separate prin spatiu. ".format(inp.name))
                sys.exit(-1)

    # liniile fisierului pana la linia "__cuvinte__" trebuie sa contina doar litere si simbolurile pt. butoane
    for linie in l:
        for i in range(0, len(linie), 2):
            if not(linie[i].islower()) and (linie[i] not in ['@', '^', '#', '>']):
                print("Input error in fisierul {0}! Caracter necunoscut in input. ".format(inp.name))
                sys.exit(-1)

    # sa existe cel putin un cuvant de cautat
    if len(cuvinte) == 0:
        print("Input error in fisierul {0}! Nu exista cuvinte de cautat. ".format(inp.name))
        sys.exit(-1)


    # verific daca problema e fara solutii
    # găsirea unui mod de a realiza din starea initială că problema nu are soluții.
    # - daca lungimea unuia dintre cuvinte este mai mare decat max(nr linii, nr coloane)
    # - daca vreunul dintre cuvinte contine o litera care nu se gaseste in matrice

    set_matrice = {y for linie in mat for y in linie}  # formeaza un set cu literele din matrice
    set_cuvinte = {x for cuv in cuvinte for x in cuv}  # formeaza un set cu literele cuvintelor de cautat in matrice
    cel_mai_lung_cuv = max(cuvinte, key=len) #cel mai lung cuvant de cautat
    # testeaza conditiile de validare
    if len(cel_mai_lung_cuv) > max(len(mat), len(mat[0])) or len(set_cuvinte - set_matrice) > 0:
        for out in [out_bf_df_dfi, out_astar, out_astar_optim, out_idastar]:
            out.write("Input fara solutii!")
            out.close
        return

    # starea initiala
    start = mat
    Graph.timeout = timeout
    Graph.nsol = nsol

    breadth_first(start, cuvinte, out_bf_df_dfi)
    #depth_first(start, cuvinte, out_bf_df_dfi)

    for eur in ["banala", "admisibila_1", "neadmisibila"]:
        a_star(start, cuvinte, out_astar, euristica=eur)
        a_star_optim(start, cuvinte, out_astar_optim, euristica=eur)
        ida_star(start, cuvinte, out_idastar, euristica=eur)


if __name__ == "__main__":
    main(sys.argv[1:])