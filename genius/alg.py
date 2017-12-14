# -*- coding: utf-8 -*-
import json
from glob import glob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dataset.fetch import songFileName
import numpy as np
import Queue as q
import config as c

def init():
    """
    Legge il dizionario da values.dic, in formato JSON,
    e lo restituisce come dizionario di Python.

    """
    try:
        # leggo dizionario 'values' da file VALUES
        with open(c.VALUES, 'r') as dic:
            values = json.load(dic)
            dic.close()
    except IOError:
        print "ERRORE: impossibile trovare il file", c.VALUES
        print "Crearne uno nuovo e effettuare il training"
        exit(1)
    except ValueError:
        print "ERRORE: il file", c.VALUES, "non è formattato come JSON."
        print "E' necessario effettuare il training"
        exit(0)

    return values

def valuta(l):

    """
    La valutazione delle frasi viene effettuata in queseto modo:

        ## si esegue, con il pacchetto vaderSentiment, un'Analisi di Sentimento dell'intera canzone
        ## si divide la canzone in righe, si analizza ogni singola riga e si ricava la media dei valori osservati
        ## si calcola poi la varianza dei valori delle singole righe

    Questo procedimento viene ripetuto allo stesso modo sui testi di canzoni e sull'input dell'utente,
    quindi si potranno confrontare i tre dizionari ottenuti da ogni analisi (val_completa, media e var) per
    determinare la somiglianza fra due testi

    """

    trainer = SentimentIntensityAnalyzer()

    # dizionario che conterrà la media dei valori osservati
    media = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

    # dizionario che conterrà la varianza dei valori osservati
    var = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

    ## valutazione della canzone nel suo insieme
    val_completa = trainer.polarity_scores(l)

    valori = [val_completa, var]

    if l != "":
    ## divisione in righe e calcolo della media:
        dim = len(l)
        val_righe = []
        i = 0

        while i < dim:
            inizioRiga = i
            while i < dim and l[i] != '\n':
                i += 1
            i += 1
            rigaCorrente = l[inizioRiga : i]
            if rigaCorrente != "\n":
                val = trainer.polarity_scores( rigaCorrente )
                val_righe.append( val )

                # sommo i valori osservati nelle singole righe per calcolare la media
                media['neg'] += val['neg']
                media['neu'] += val['neu']
                media['pos'] += val['pos']
                media['compound'] += val['compound']

        N = len(val_righe)

        if N > 0:
        # divido per il numero di righe della frase e ottengo la media:
            media['neg'] /= N
            media['neu'] /= N
            media['pos'] /= N
            media['compound'] /= N

    ## calcolo della varianza: somma degli scarti al quadrato
        for val in val_righe:
            var['neg'] += (val['neg'] - media['neg']) ** 2
            var['neu'] += (val['neu'] - media['neu']) ** 2
            var['pos'] += (val['pos'] - media['pos']) ** 2
            var['compound'] += (val['compound'] - media['compound']) ** 2

        if N > 0:
        # divido per il numero di righe della frase e ottengo la varianza:
            var['neg'] /= N
            var['neu'] /= N
            var['pos'] /= N
            var['compound'] /= N

        valori = [val_completa, var]
    return valori

def train():
    """
    Calcola e salva un dizionario nella forma:

        { ...
             "Artista_Titolo traccia": [{ valutazione completa }, { varianza }],
        ... }

    contenente i risultati della funzione 'valuta()' per ogni canzone del dataset
    e lo salva nel file values.dic, sovrascrivendone il contenuto.

    """

    confirm = raw_input("Quest'operazione cancellera' e ricalcolera' il contenuto del file 'values.dic'. L'operazione puo' richiedere alcuni minuti. Continuare?\n[s/N] >>> ")
    # confirm = 's'     # per saltare la conferma

    if confirm == 's':
        ## ricalcolo dizionario
        V = {}

        files = glob(c.SONGS + '/*.lyr')# cerco all'interno della cartella delle canzoni tutti i file con estensione .lyr

        header = {}                     # dizionario che contiene, per ogni file letto, le informazioni sulla canzone

        i = 0                           # contatore
        for fname in files:
            with open(fname, 'r') as lyricfile:
                # leggo informazioni canzone
                header = eval(lyricfile.readline())

                # leggo da file il testo, ignorando le righe che iniziano con /* (righe mancanti dal testo della canzone)
                # sartando le canzoni che hanno meno di 10 righe di testo
                lyrics = ""
                lines_count = 0
                for line in lyricfile:
                    if line[0:2] != '/*':
                        lyrics += line
                        if line[0] != '\n':
                            lines_count += 1

                if lines_count > 10:
                # calcolo i valori per la canzone corrente e li salvo nel dizionario
                    values = valuta(lyrics)

                    key = __getKey__(header)
                    V[key] = values

                    lyricfile.close()
                    i += 1

                if (i % 1000) == 0:
                    print "Read", i, "songs..."

        print "Finished.", i, "songs read."
        try:
        ## salvo il nuovo dizionario nel file values.dic
            with open(c.VALUES, 'w') as value_file:
                json.dump(V, value_file, indent=4)
                value_file.close()
        except IOError:
            print "ERRORE:", "impossibile trovare il file", c.VALUES
            print "Crearne uno nuovo e effettuare il training"
            exit(1)
    else:
        V = init()
        print "Operazione annullata. E' stato caricato il valore corrente salvato in 'values.dic'."

    ## restituisco matrice di valori appena calcolata
    return V

def __getKey__(header):
    """
    Calcola la chiave del dataset per una canzone a partire dall'header
    che ne contiene i metadati (in questa implementazione: 'artista' e 'titolo')
    """

    return (songFileName(header['artista'], header['titolo'])).encode()

def __distanza__(val1, val2):
    """
    Calcola la differenza fra due valutazioni di sentiment analysis effettuate
    da VADER.

    """

    val1_completa = val1[0]
    val2_completa = val2[0]

    diff_pos = val1_completa['pos'] - val2_completa['pos']
    diff_neu = val1_completa['neu'] - val2_completa['neu']
    diff_neg = val1_completa['neg'] - val2_completa['neg']

    coeff_compound = 1 + abs(val1_completa['compound'] - val2_completa['compound'])

    return (diff_pos ** 2 + diff_neu **2 + diff_neg ** 2) * coeff_compound

def cerca(userinputvalues, dic = {}, ris_n = 1):
    """
    Confronta i valori dell'input utente con quelli derivati dalle canzoni,
    presenti nel dizionario 'dic' (che di default viene caricato dal file values.dic,
    ma è possibile specificare un altro insieme di valori con mat=altro_dizionario)
    e restituisce una lista di risultati, contenente 'ris_n' coppie ('chiave', 'valore').
    'ris_n' di default vale 1.
    """

    if dic == {}:
        dic = init()

    risultati = q.Queue(maxsize=ris_n)          # lista di risultati

    items = dic.items()       # trasformo il contenuto di dic in una lista di coppie ('chiave', 'valore')
    np.random.shuffle(items)

    ## cerco il valore medio tra le distanze tra input e canzone
    somma_dist = 0
    for song in items:
        somma_dist += __distanza__(userinputvalues, song[1])
    soglia = somma_dist / len(items)

    ## cerco la canzone con distanza minima da userinputvalues
    distanza_min = __distanza__(userinputvalues, items[0][1])  # calcolo prima distanza

    for song in items:
        # separo chiave e valore
        chiave = song[0]        # nome del file delle lyrics
        valore = song[1]        # lista dei dizionari retituiti da valuta()
        varianza = valore[1]['compound']    # = song[1][1]['compound]

        distanza_corrente = __distanza__(userinputvalues, valore)

        # aggiusto la distanza con il valore di varianza
        if distanza_corrente < soglia:
            distanza_corrente *= 1 + varianza
        else:
            distanza_corrente *= 1 - varianza

        if distanza_corrente <= distanza_min:
            # nuovo minimo trovato: svuoto lista risultati
            distanza_min = distanza_corrente
            if risultati.full():
                risultati.get()
            risultati.put(chiave)

    # estraggo risultati dalla coda
    ris_list = []
    while (not risultati.empty()):
        ris_list.insert(0, risultati.get())

    return ris_list
