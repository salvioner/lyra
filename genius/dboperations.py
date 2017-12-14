# -*- coding: utf-8 -*-
from alg import init
import config as c
from dataset.fetch import songFileName
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from glob import glob
import os

def cluster(dic = {}):
    """
    Esegue il clustering di dic (di default dic è il dizionario contenuto in
    values.dic) in base al sentimento (pos, neg, neu) e mostra il grafico dei
    cluster così ottenuti

    """
    if dic == {}:
        dic = init()

    POS = 0
    NEU = 1
    NEG = 2

    items = dic.items()
    np.random.shuffle(items)
    N = len(items)

    D = np.zeros( (N, 3) )

    print "Clustering..."

    for i in range(N):
        song = items[i]
        valori = song[1]
        val_completa = valori[0]

        D[i][POS] = val_completa['pos']
        D[i][NEU] = val_completa['neu']
        D[i][NEG] = val_completa['neg']

    centers_array = np.zeros((3,3))
    centers_array[POS] = [1, 0, 0]
    centers_array[NEU] = [0, 1, 0]
    centers_array[NEG] = [0, 0, 1]

    centers = np.ndarray((3, 3), buffer=centers_array)

    kmeans = KMeans(n_clusters=3, init=centers, n_init=1).fit(D)

    print "Done."

    X = np.zeros(N)
    Y = np.zeros(N)

    for i in range(N):
        X[i] = D[i][NEG]
        Y[i] = D[i][POS]

    cluster = kmeans.labels_

    plt.scatter(X, Y, c=cluster)

    axes = plt.gca()
    axes.set_xlim([0, 0.8])
    axes.set_ylim([0, 0.8])

    plt.title("Distribuzione delle canzoni all'interno del database")
    plt.ylabel("punteggio 'pos'", color='blue')
    plt.xlabel("punteggio 'neg'", color='red')

    plt.text(0.275, 0.575, "Il punteggio 'neu' e' una funzione degli altri due\ne si calcola come:\n1 - 'pos' - 'neg'\nLe canzoni piu' neutrali (cluster verde)\nsono quelle piu' vicine all'origine degli assi.")

    plt.show()
