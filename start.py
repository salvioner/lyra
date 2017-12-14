# -*- coding: utf-8 -*-

"""
Questo file contiene i comandi di base per l'istruzione e l'avvio
del tool

"""
import genius.alg as g
import genius.config as c
import genius.dboperations as db
from sys import argv

""" FUNZIONI """

def printHeader():
    print "Lyra - un motore di ricerca di testi di canzoni basato su sentiment analysis."
    print ""
    print "This tool uses VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text"
    print "by C.J. Hutto and Eric Gilbert, E.E. (2014)"
    print "Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014."
    print "Created in 2016 by Arighi Andrea and Tosin Riccardo"
    print "Run 'python start.py -h' for help."
    print ""

def printHelp():
    print "\tUtilizzo: python start.py [Opzioni]"
    print ""
    print "Opzioni:"
    print "\t-h\t\tMostra questo aiuto"
    print "\t-t\t\tRicalcola i valori di tutto il dataset"
    print "\t-i <testo>\tEsegue la ricerca in base al <testo>"
    print "\t-r <n>\t\tRestituisce i primi <n> risultati ordinati secondo l'affinità con l'input"
    print "\t-c\t\tEsegue l'algoritmo di clustering K-Means dell'intero dataset e mostra il grafico corrispondente (ignora l'input)"
    print ""

def getOptions(ops):
    """
    Legge le opzioni da sys.argv e setta i valori nel dizionario 'ops'
    """

    argc = len(argv)
    if argc == 1:
        printHeader()

    i = 1
    while i < argc:

        o = argv[i]

        if o[0] != "-":
            ops["valid"] = False
        elif o == "-h":
            ops["help"] = True

        if ops["valid"] == True and ops["help"] == False:
            if o == "-t":
                ops["train"] = True
            elif o == "-i":
                i += 1
                ops["input"] = argv[i]
            elif o == "-r":
                i += 1
                try:
                    ris_n = int(argv[i])
                except ValueError:
                    ops["valid"] = False
                else:
                    ops["ris_n"] = ris_n
            elif o == "-c":
                ops["cluster"] = True
        else:
            break

        i += 1

    return


""" PROGRAMMA """

options = {"valid": True, "train": False, "help": False, "input": "", "ris_n": 1, "cluster": False}

getOptions(options)

if options["valid"] == False:
    print "Input non valido.\n"
    options["help"] = True

if options["help"]:
    if options["valid"] == True:
        printHeader()           # ometto il titolo e stampo solo l'aiuto in caso di input utente non valido
    printHelp()
else:

    if options["train"]:
        valoriDataset = g.train()
        print "Training completato."
    else:
        valoriDataset = g.init()

    if options["cluster"] == False:

        # leggi input utente
        if options["input"] == "" or options["input"] == " " or options["input"] == "\n":
            testoUtente = raw_input("Inserire una frase, un testo, uno stato d'animo...\n(in inglese) >>> ")
            print ""
        else:
            testoUtente = options["input"]

        # esegui sentiment analysis sull'input utente utilizzando la stessa funzione
        # con cui è stata effettuata sui testi dl dataset
        valoriUtente = g.valuta(testoUtente)

        # ricerca nella matrice di valori del dataset la canzone che si avvicina di più
        # all'input fornito
        match = g.cerca(valoriUtente, dic = valoriDataset, ris_n = options["ris_n"])

        i = 0
        matches = len(match)
        if matches > 1:
            print "trovati", matches,"risultati:"
            for k in range( matches ):
                print "\t" + str(k+1), "-", match[k]

            try:
                i = int(raw_input("Quale testo devo visualizzare?\n(1 - " + str(matches) + ") >>> "))
            except ValueError:
                i = -1

            while (i-1) not in range(matches):
                try:
                    i = int(raw_input("Fuori intervallo. Inserire un numero tra 1 e " + str(matches) + "\n>>> "))
                except ValueError:
                    i = -1

            i -= 1

        songpath = str(c.SONGS + "/" + match[i])
        with open(songpath, 'r') as lyrics:
            header = {}

            for line in lyrics:
                if header == {}:
                    header = eval(line)
                    print "La tua canzone e':\n", header["titolo"], "-", header["artista"]
                    print "(dall'album", header["album"] + ")"
                else:
                    print line

            lyrics.close()

    else:

        db.cluster(dic = valoriDataset)

raw_input("\n*** Premi Invio per uscire ***")
