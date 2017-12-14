# -*- coding: utf-8 -*-

# Given a list of artists in 'INPUT' file, fetch all the
# Wikipedia page titles for those artists' albums and saves them to 'OUTPUT'

import os
from wikiparser import wp, utils
from fetch import getFetchedTitle, filterTagNameSequence, getParagraphById
from urllib2 import Request, urlopen, URLError
from bs4 import BeautifulSoup
import codecs as cod

""""""""" SETUP E VAR GLOBALI """""""""
# percorsi files

wdir = os.path.dirname(__file__)

MISSING = os.path.join(wdir, 'albums/MISSING_ARTISTS.txt')
OUTPUT = os.path.join(wdir, 'albums/albums.list')
INPUT = [os.path.join(wdir, 'artists/artists.list')]

# reset file MISSING_ARTISTS e OUTPUT
def resetFiles():
    fout = open(MISSING, 'w')
    fout.close()
    fout = open(OUTPUT, 'w')
    fout.close()

COUNT = 0
CONNECTION_REQUESTS_LIMIT = 10

""""""""" FUNZIONI """""""""
    
def setMissing(artist):
    # aggiungi 'artist' al file degli artisti non trovati
    with open(MISSING, 'a') as fout:
        fout.write(artist + ",\n")
        fout.close()

def fetch(title):
    global COUNT
    
    # creo l'URL di wikipedia col titolo corrispondente
    url = wp.WParse(title)
    # creo la richiesta del sito
    req = Request(url)
    
    try:
        html = ''
        con_req = 0
        while html == '' and con_req < CONNECTION_REQUESTS_LIMIT:
            # connetto alla pagina
            html = urlopen(req)
            con_req += 1
    except URLError as e:
        print "ERROR while fetching", url
        # errore nella rihiesta
        if hasattr(e, 'reason'):
            # errore di connessione - URL
            print 'Pagina irraggiungibile.'
            print 'Reason: ', e.reason, "\n"
            # restituisci valore positivo - errore di connettività
            return 1
        elif hasattr(e, 'code'):
            # errore dal server
            print 'Il server non ha potuto processare la richiesta.'
            print 'Error code: ', e.code
            # restituisci valore negativo - indica che la pagina corrente non è stata trovata ma che non ci sono errori di connettività
            return -1
        print "\n"
    else:    
        if html == '':
            print title, "- pagina vuota"
            # restituisci valore negativo - indica che la pagina corrente non è stata trovata ma che non ci sono errori di connettività
            return -1
            
        
        # la richiesta è andata a buon fine
        document = html.read(size=-1)
        soup = BeautifulSoup(document, 'html.parser')
        """
        ** ITA **
        I titoli degli album si trovano dentro il <div> con id="Discografia",
        all'interno di questa sequenza di tag:
            
        <div id="Discografia">    
            <ul>
                <li>
                    <i>
                        <a ... title="Titolo Album"> ALBUM TITLE </a>
                    </i>
                </li>
            </ul>
        </div>
        
        Eseguo quindi il parsing della pagina per trovare la lista degli
        album di ogni artista.
        
        ** ENG **
        Album titles are found inside the only <div> element with the id
        "Discografia" on the Italian Wikipedia; within that <div> there is a structure like this:
            
        <div id="Discografia">    
            <ul>
                <li>
                    <i>
                        <a ... title="Titolo Album"> ALBUM TITLE </a>
                    </i>
                </li>
            </ul>
        </div>
        
        Now the page is parsed to isolate this structure and, more precisely,
        the album title. The procedure is repeatd for every artist.
    
        """
        
        # Isolo il paragrafo relativo all'id "Discografia"
        #
        # Finding the element with id "Discografia"
        par = getParagraphById(soup.body, "Discografia")
        if par == []:
            par = getParagraphById(soup.body, "Discografia_parziale")
        if par == []:
            par = getParagraphById(soup.body, "Discografia_essenziale")
        if par == []:
            return -1
        
        
        # il filtro restituisce ogni <a> che si trova all'interno di un <i> 
        # che stia all'interno di un <li>:
        #
        # this filter returns the list of the <a> elements which are inside
        # an <i> element which is inside a <li> element:
        nodes = filterTagNameSequence(['li', 'i', 'a'], par)
        # salvo in un vettore il valore degli attributi "title", ovvero i
        # titoli delle pagine di  wikipedia di riferimento
        #
        # saving all album names (their titles from the italian Wikipedia)
        # inside an array and checking if they are valid WP page names.
        albums = []
        for n in nodes:
            if n.has_key("title"):
                page = n["title"]
                if utils.exists(page):
                    albums.append(page)
                    COUNT += 1
        # aggiorno file degli album
        # 
        # updating albums file
        fout = cod.open(OUTPUT, 'a', 'utf-8-sig')
        for a in albums:
            fout.write(a + "\n")
        fout.close()
        print title, "- album aggiunti"
        return 0



""""""""" PROGRAMMA """""""""

# apertura file input
for input_file in INPUT:
    with open(input_file, "r") as fin:
        print "lista aperta:", input_file, "\n"
        # setup del wiki url parser
        wp.setLanguage("it")
        
        # analisi del file
        for line in fin:
            print "\n"
            
            # leggo il titolo dal file ed elimino eventuali caratteri di fine riga
            title = getFetchedTitle(line)
            
            for t in [title, title + " (gruppo musicale)", title + " (cantante)"]:
                retval = fetch(t)
                if retval == 0:
                    #album trovati correttamente
                    break
            
            if retval != 0:
                # aggiungi artista al file degli artisti non trovati
                setMissing(getFetchedTitle(line))
        fin.close()
        
print "\n", "Album trovati:", COUNT