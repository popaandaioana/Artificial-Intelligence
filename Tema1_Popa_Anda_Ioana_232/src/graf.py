import copy
import sys
import time


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    out = None
    def __init__(self, id, info, parinte, cost=0, buton = None, h=0):
        self.id = id #numarul de ordine al nodului din arbore
        self.info = info #informatia din nod (matricea)
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  #costul din nodul start pana in nodul curent
        self.h = h #costul estimat pana intr-un nod scop
        self.f = self.g + self.h
        self.buton = buton #butonul si modul in care a fost activat pt a obtine acest nod (sau None pt nod start)


    #obtine drumul de la radacina la nodul curent
    # param = un nod de tipul NodParcurgere
    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte) #parintele nodului curent este inserat in lista inaintea fiului
            nod = nod.parinte
        return l


    #trebuie si pt. dfi (nr. total noduri si nr. max noduri)
    #param : un nod de tipul NodParcurgere si ida_max
    #functia returneaza si lungimea drumului
    def afisDrum(self, ida_max=None):
        global max_ida
        stop_time = time.time() #termina de masurat timpul pana a ajuns la solutie
        l = self.obtineDrum() #lista nodurilor din solutie (drumul de afisat)
        butoane = [x.buton for x in l] #lista cu butoanele + mod de activare pentru acest drum (string)
        lg = len(l) #cate noduri am in drumul de afisat

        #pt. fiecare nod din drum, scrie in output conform formatului cerut
        for i in range(lg):
            NodParcurgere.out.write("{0})\n".format(i + 1))
            for row in l[i].info:
                NodParcurgere.out.write("{0}\n".format(' '.join([str(a) for a in row])))  # reprez. si scriere matrice in fisier
            #pt. nodurile cu exceptia ultimului scriu in  fisier si textul de activare
            if i != lg - 1:
                NodParcurgere.out.write(str(butoane[i + 1]) + "\n")

        NodParcurgere.out.write("\n\n")
        NodParcurgere.out.write("Lungime drum: " + str(lg - 1) + '\n') #lungime drum = nr muchii = nr. noduri - 1
        NodParcurgere.out.write("Cost drum: " + str(self.f) + '\n')
        NodParcurgere.out.write("Timp gasire solutie: " + str(round(1000 * (stop_time - Graph.start_time))) + 'ms\n')

        maxim = Graph.maxim if ida_max is None else ida_max
        NodParcurgere.out.write("Nr noduri maxim existente in memorie: " + str(maxim) + '\n')
        NodParcurgere.out.write("Nr total noduri calculate: " + str(Graph.noduriTotale) + '\n')
        NodParcurgere.out.write("\n------------\n")
        return len(l)

    # verifica daca pe drumul de la nodul curent la radacina apare un nod deja existent
    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

#------------------------------------------------------------------------------------------------------------------


class Graph:
    """Graful efectiv al problemei
    """
    noduriTotale = 0
    start_time = 0
    timeout = 0
    nsol = 0
    maxim = 0

    def __init__(self, start, cuvinte, euristica: str = "banala"):
        self.euristica = euristica
        self.start = start #starea initiala
        self.cuvinte = cuvinte #lista cuvintelor care trebuie formate in matrice
        Graph.noduriTotale = 0 #nr. total noduri calculate
        Graph.maxim = 0 #nr. maxim de noduri existente in memorie
        Graph.start_time = time.time()


    # param: informatia unui nod de tip NodParcurgere
    # Formez o lista cu toate cuvintele din matrice ( oriz + varticala). Transform lista intr-un string
    #in care cuv sunt separate prin spatiu. Apoi testez daca fiecare cuvant de cautat este subsir al acestui sir format
    def testeaza_scop(self, InfoNodCurent):
        lista_orizontala_verticala = [] #lista cu sirurile de pe linii si coloane ( toate cuv. din matrice)
        for i in range(len(InfoNodCurent)):
            lista_orizontala_verticala.append("".join(InfoNodCurent[i]))
        for j in range(len(InfoNodCurent[0])):
            cuvant = ""
            for i in range(len(InfoNodCurent)):
                cuvant = cuvant + str(InfoNodCurent[i][j])
            lista_orizontala_verticala.append(cuvant)
        sir_cuvinte_matrice = "" #sir cu sirurile de pe linii si coloane separate prin spatiu
        for i in range(len(lista_orizontala_verticala)):
            sir_cuvinte_matrice = sir_cuvinte_matrice + " " + lista_orizontala_verticala[i]

        for elem in self.cuvinte:
            if elem not in sir_cuvinte_matrice:
                return 0
        return 1

    # functie care calculeaza cate cuvinte s-au format la un mom. dat in matrice din cele de cautat
    def nr_cuv_formate(self, InfoNodCurent):
        lista_orizontala_verticala = [] #lista cu sirurile de pe linii si coloane
        for i in range(len(InfoNodCurent)):
            lista_orizontala_verticala.append("".join(InfoNodCurent[i]))
        for j in range(len(InfoNodCurent[0])):
            cuvant = ""
            for i in range(len(InfoNodCurent)):
                cuvant = cuvant + str(InfoNodCurent[i][j])
            lista_orizontala_verticala.append(cuvant)
        sir_cuvinte_matrice = "" #sir cu sirurile de pe linii si coloane separate prin spatiu
        for i in range(len(lista_orizontala_verticala)):
            sir_cuvinte_matrice = sir_cuvinte_matrice + " " + lista_orizontala_verticala[i]

        nr_cuv = 0
        for elem in self.cuvinte:
            if elem in sir_cuvinte_matrice:
                nr_cuv = nr_cuv + 1
        return nr_cuv


    def genereazaSuccesori(self, nodCurent):
        """Genereaza succesori.
        Activand pentru nodCurent un buton obtin o alta stare.
        Costul activarii depinde de buton si de modalitatea de activare a acestuia.
        Determin toate starile in care se poate ajunge din nodul nodCurent.
        Args:
            nodCurent (NodParcurgere): Nodul unde ma aflu momentan in arbore
        Returns:
            [NodParcurgere]: Lista succesorilor nodului curent.
        """

        listaSuccesori = []
        mat = nodCurent.info #pentru mat trebuie sa generam toti succesorii
        # parcurg matricea si vad unde am buton
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                if mat[i][j] in ['@', '#', '>', '^']:
                    btn = mat[i][j]
                    # daca butonul = @, calc. cati vecini are in jur (costul)
                    if (btn == '@'):
                        # lista_vecini invartitor: lista de liste de triplete de forma : ind. linie, ind. col., valoare
                        litere_vecini_invartitor = []
                        # in if-uri verific sa nu iasa din matrice si sa fie litera
                        if i - 1 >= 0 and j - 1 >= 0 and mat[i - 1][j - 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i - 1, j - 1, mat[i - 1][j - 1]])
                        if j - 1 >= 0 and mat[i][j - 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i, j - 1, mat[i][j - 1]])
                        if i + 1 < len(mat) and j - 1 >= 0 and mat[i + 1][j - 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i + 1, j - 1, mat[i + 1][j - 1]])
                        if i + 1 < len(mat) and mat[i + 1][j] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i + 1, j, mat[i + 1][j]])
                        if i + 1 < len(mat) and j + 1 < len(mat[0]) and mat[i + 1][j + 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i + 1, j + 1, mat[i + 1][j + 1]])
                        if j + 1 < len(mat[0]) and mat[i][j + 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i, j + 1, mat[i][j + 1]])
                        if i - 1 >= 0 and j + 1 < len(mat[0]) and mat[i - 1][j + 1] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i - 1, j + 1, mat[i - 1][j + 1]])
                        if i - 1 >= 0 and mat[i - 1][j] not in ['@', '#', '>', '^']:
                            litere_vecini_invartitor.append([i - 1, j, mat[i - 1][j]])

                        # daca butonul are mai mult de o litera vecina
                        if len(litere_vecini_invartitor) > 1:
                            litere_vecini_invartitor_stanga = copy.deepcopy(litere_vecini_invartitor)
                            # rotire la stanga:
                            mat_stanga = copy.deepcopy(mat)
                            # in aux salvez litera care se pierde in momentul rotirii
                            aux = litere_vecini_invartitor_stanga[len(litere_vecini_invartitor_stanga) - 1][2]
                            for i in range(len(litere_vecini_invartitor_stanga) - 1, 0, -1):
                                litere_vecini_invartitor_stanga[i][2] = litere_vecini_invartitor_stanga[i - 1][2]
                            #il pun si pe aux pe poz. corespunzatoare
                            litere_vecini_invartitor_stanga[0][2] = aux

                            # actualizare matrice cu elementele rotite
                            for elem in litere_vecini_invartitor_stanga:
                                mat_stanga[elem[0]][elem[1]] = elem[2]
                            msg = "Activare invartitor stanga"
                            # daca acest succesor nu se afla deja in lista, il adaug in lista de succesori
                            if not nodCurent.contineInDrum(mat_stanga):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_stanga, nodCurent, nodCurent.g + len(litere_vecini_invartitor), msg, h = self.calculeaza_h(mat_stanga))
                                listaSuccesori.append(nodSuccesor)


                            litere_vecini_invartitor_dreapta = copy.deepcopy(litere_vecini_invartitor)
                            # rotire la dreapta:
                            mat_dreapta = copy.deepcopy(mat)
                            aux = litere_vecini_invartitor_dreapta[0][2]
                            for i in range(len(litere_vecini_invartitor_dreapta) - 1):
                                litere_vecini_invartitor_dreapta[i][2] = litere_vecini_invartitor_dreapta[i + 1][2]
                            litere_vecini_invartitor_dreapta[len(litere_vecini_invartitor_dreapta) - 1][2] = aux

                            for elem in litere_vecini_invartitor_dreapta:
                                mat_dreapta[elem[0]][elem[1]] = elem[2]
                            msg = "Activare invartitor dreapta"
                            if not nodCurent.contineInDrum(mat_dreapta):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_dreapta, nodCurent, nodCurent.g + len(litere_vecini_invartitor), msg, h = self.calculeaza_h(mat_dreapta))
                                listaSuccesori.append(nodSuccesor)

                    # cost = 2 (constant)
                    if (btn == '#'):
                        # sus_jos
                        mat_interschimbator = copy.deepcopy(mat)
                        # in if-uri verific sa nu iasa din matrice si sa fie litera
                        if (i - 1 >= 0 and i + 1 < len(mat_interschimbator) and mat_interschimbator[i - 1][j] not in ['@', '#', '^', '>'] and mat_interschimbator[i + 1][j] not in ['@', '#', '^', '>']):
                            # se face interschimbarea sus- jos
                            mat_interschimbator[i - 1][j], mat_interschimbator[i + 1][j] = mat_interschimbator[i + 1][j], mat_interschimbator[i - 1][j]
                            msg = "Activare interschimbator sus-jos"
                            # daca acest succesor nu se afla deja in lista, il adaug in lista de succesori
                            if not nodCurent.contineInDrum(mat_interschimbator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_interschimbator, nodCurent, nodCurent.g + 2, msg, h = self.calculeaza_h(mat_interschimbator))
                                listaSuccesori.append(nodSuccesor)

                        # stanga_dreapta
                        mat_interschimbator = copy.deepcopy(mat)
                        if (j - 1 >= 0 and j + 1 < len(mat_interschimbator[0]) and mat_interschimbator[i][j - 1] not in ['@', '#', '^', '>'] and mat_interschimbator[i][j + 1] not in ['@', '#','^', '>']):
                            mat_interschimbator[i][j - 1], mat_interschimbator[i][j + 1] = mat_interschimbator[i][j + 1], mat_interschimbator[i][j - 1]
                            msg = "Activare interschimbator stanga-dreapta"
                            if not nodCurent.contineInDrum(mat_interschimbator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_interschimbator, nodCurent, nodCurent.g + 2, msg, h = self.calculeaza_h(mat_interschimbator))
                                listaSuccesori.append(nodSuccesor)

                        # stanga-sus_dreapta-jos
                        mat_interschimbator = copy.deepcopy(mat)
                        if j - 1 >= 0 and j + 1 < len(mat_interschimbator[0]) and i - 1 >= 0 and i + 1 < len(mat_interschimbator) and mat_interschimbator[i - 1][j - 1] not in ['@', '#','^', '>'] and mat_interschimbator[i + 1][j + 1] not in ['@', '#', '^', '>']:
                            mat_interschimbator[i - 1][j - 1], mat_interschimbator[i + 1][j + 1] = mat_interschimbator[i + 1][j + 1], mat_interschimbator[i - 1][j - 1]
                            msg = "Activare interschimbator stanga-sus_dreapta-jos"
                            if not nodCurent.contineInDrum(mat_interschimbator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_interschimbator, nodCurent, nodCurent.g + 2, msg, h = self.calculeaza_h(mat_interschimbator))
                                listaSuccesori.append(nodSuccesor)

                        # dreapta-sus_stanga-jos
                        mat_interschimbator = copy.deepcopy(mat)
                        if j - 1 >= 0 and j + 1 < len(mat_interschimbator[0]) and i - 1 >= 0 and i + 1 < len(mat_interschimbator) and mat_interschimbator[i - 1][j + 1] not in ['@', '#', '^', '>'] and mat_interschimbator[i + 1][j - 1] not in ['@', '#', '^', '>']:
                            mat_interschimbator[i - 1][j + 1], mat_interschimbator[i + 1][j - 1] = mat_interschimbator[i + 1][j - 1], mat_interschimbator[i - 1][j + 1]
                            msg = "Activare interschimbator dreapta-sus_stanga-jos"
                            if not nodCurent.contineInDrum(mat_interschimbator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_interschimbator, nodCurent, nodCurent.g + 2, msg, h = self.calculeaza_h(mat_interschimbator))
                                listaSuccesori.append(nodSuccesor)

                    # cost = nr. poz. cu care sunt deplasate literele
                    if (btn == '^'):
                        #nr_butone de pe coloana lui ^
                        nr_butoane = 0
                        for k in range(len(mat)):
                            if mat[k][j] in ['@', '#', '^', '>']:
                                nr_butoane = nr_butoane + 1

                        # k = nr. maxim de pozitii cu care se pot muta literele de pe col. urcatorului
                        k = len(mat) - nr_butoane - 1
                        lista_litere_col_urcator = [] #lista cu literele si indicii lor de pe col. urcatorului (fara butoane)
                        for ind in range(len(mat)):
                            if mat[ind][j] not in ['@', '#', '^', '>']:
                                lista_litere_col_urcator.append([ind, j, mat[ind][j]])

                        mat_urcator = copy.deepcopy(mat)
                        for x in range(1, k + 1):
                            # urc cate o pozitie de k ori
                            aux = lista_litere_col_urcator[0][2]
                            # se realizeaza deplasarea literelor
                            for y in range(1, len(lista_litere_col_urcator)):
                                lista_litere_col_urcator[y - 1][2] = lista_litere_col_urcator[y][2]
                            lista_litere_col_urcator[len(lista_litere_col_urcator) - 1][2] = aux
                            # actualizare matrice cu elementele deplasate
                            for elem in lista_litere_col_urcator:
                                mat_urcator[elem[0]][elem[1]] = elem[2]
                            msg = "Activare urcator cu " + str(x) + " pasi"
                            # daca acest succesor nu se afla deja in lista, il adaug in lista de succesori
                            if not nodCurent.contineInDrum(mat_urcator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_urcator, nodCurent, nodCurent.g + x, msg, h = self.calculeaza_h(mat_urcator))
                                listaSuccesori.append(nodSuccesor)

                    # cost = nr. poz. cu care sunt deplasate literele
                    if (btn == '>'):
                        #nr. de butoane de pe linia lui >
                        nr_butoane = 0
                        for k in range(len(mat[0])):
                            if mat[i][k] in ['@', '#', '^', '>']:
                                nr_butoane = nr_butoane + 1

                        # k = nr. maxim de pozitii cu care se pot muta literele de pe linia dreptatorului
                        k = len(mat[0]) - nr_butoane - 1
                        lista_litere_lin_dreptator = []
                        for ind in range(len(mat[0])):
                            if mat[i][ind] not in ['@', '#', '^', '>']:
                                lista_litere_lin_dreptator.append([i, ind, mat[i][ind]])

                        mat_dreptator = copy.deepcopy(mat)

                        for x in range(1, k + 1):
                            # deplasez la dreapta cate o pozitie de k ori
                            aux = lista_litere_lin_dreptator[len(lista_litere_lin_dreptator) - 1][2]
                            # se realizeaza deplasarea literelor
                            for y in range(len(lista_litere_lin_dreptator) - 1, 0, -1):
                                lista_litere_lin_dreptator[y][2] = lista_litere_lin_dreptator[y - 1][2]
                            lista_litere_lin_dreptator[0][2] = aux
                            for elem in lista_litere_lin_dreptator:
                                mat_dreptator[elem[0]][elem[1]] = elem[2]
                            msg = "Activare dreptator cu " + str(x) + " pasi"
                            # daca acest succesor nu se afla deja in lista, il adaug in lista de succesori
                            if not nodCurent.contineInDrum(mat_dreptator):
                                nodSuccesor = NodParcurgere(nodCurent.id + 1, mat_dreptator, nodCurent, nodCurent.g + x, msg, h = self.calculeaza_h(mat_dreptator))
                                listaSuccesori.append(nodSuccesor)


        # la nodurile totale calculate se adauga succesorii
        Graph.noduriTotale += len(listaSuccesori)
        return listaSuccesori

    def calculeaza_h(self, mat):
        #nr. butoane din matrice
        nr_butoane = 0
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                if mat[i][j] in ['@', '#', '^', '>']:
                    nr_butoane = nr_butoane + 1
        # costul maxim pe care poate sa il aiba fiecare buton
        cost_maxim_urcator = len(mat) - nr_butoane - 1
        cost_maxim_dreptator = len(mat[0]) - nr_butoane - 1
        cost_maxim_interschimbator = 2
        cost_maxim_invartitor = 8

        # banala: estimez cotul ca fiind 1 daca n-am ajuns in scop si 0 daca am ajuns
        if self.euristica == "banala":
            if self.testeaza_scop(mat):
                return 0
            return 1
        if self.euristica == "admisibila_1":
            # (numar cuv. de obtinut - numar cuv. obtinute) / nr. cuv. de obtinut
            return (len(self.cuvinte) - self.nr_cuv_formate(mat)) / len(self.cuvinte)
        #if self.euristica == "admisibila_2":
            #return (n - k) / n, unde n = nr. cuv. de obtinut si k = nr. cuv. obtinute complet / incomplet

        #neadm: indif. de butonul activat, costul estimarii este > costul real al activarii sale
        if self.euristica == "neadmisibila":
            return max(cost_maxim_urcator, cost_maxim_dreptator, cost_maxim_interschimbator, cost_maxim_invartitor) + 1
        return 0


    def __repr__(self):
        """
                Funcția de reprezentare a grafului
                :return: str
                """
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


