# -*- coding: utf-8 -*-

# Given a list of album titles in 'INPUT' file, fetch the lyrics
# from LyricsWikia for 'SONGS_TO_FETCH' songs from each album.

import os
from wikiparser import wp
from wikiparser.utils import exists
from lyricswikia.lw import LWParse, removeTagPosition
from fetch import filterTagNameSequence, getParagraphById, songFileName
from urllib2 import Request, urlopen, URLError
from bs4 import BeautifulSoup
import codecs as cod

""""""""" SETUP E VAR GLOBALI """""""""

INPUT = "albums/albums.list"     #default: albums.list - testing: test2.list
OUTPUT_FOLDER = "songs"
INDEX = os.path.join(OUTPUT_FOLDER, "index.txt")

COUNT = 0
CONNECTION_REQUESTS_LIMIT = 10
SONGS_TO_FETCH = 3

wp.setLanguage('it')

#chiudo i file eventualmente utilizzati da vecchi processi
err = 2
try:
    fin.close()
except NameError:
    err = err - 1

try:
    os.close(lyrfile)
except OSError:
    err = err - 1
except NameError:
    err = err -1

if err > 0:
    print "[closed", err, "opened files]"

""""""""" FUNZIONI """""""""

def fetchAlbumData(album):
    url = wp.WParse(album)
    req = Request(url)

    album_title = "-1"
    artist = ""
    genres = []
    tracks = []

    try:
        html = ''
        con_req = 0
        while html == '' and con_req < CONNECTION_REQUESTS_LIMIT:
            # connetto alla pagina
            html = urlopen(req)
            con_req += 1
    except UnicodeEncodeError:
        print "Couldn't read url for album", album
    except URLError as e:
        print "ERROR while fetching", url
        # errore nella rihiesta
        if hasattr(e, 'reason'):
            # errore di connessione - URL
            print 'Pagina irraggiungibile.'
            print 'Reason: ', e.reason, "\n"

        elif hasattr(e, 'code'):
            # errore dal server
            print 'Il server non ha potuto processare la richiesta.'
            print 'Error code: ', e.code
        # restituisco codice di errore -1
    else:
        if html!= '':
            # In caso questo non avvenga, restituisci valore negativo "-1" per album_title - inizializzato in alto
            # indica che la pagina corrente non è stata trovata
            # ma che non ci sono errori di connettività

            # la richiesta è andata a buon fine
            document = html.read(size=-1)
            soup = BeautifulSoup(document, 'html.parser')

            # leggo titolo album dall'intestazione della tabella; se non è possibile, lo leggo dal nome album passatomi come parametro
            testata = soup.body('tr', class_="sinottico_testata")
            album_tag = filterTagNameSequence(['th', 'i'], testata)
            if len(album_tag) > 0:
                album_title = album_tag[0].string
            else:
                album_tag = album
            # leggo nome artista
            artist_label = soup.body.find('th', string="Artista")
            if artist_label is None or (not hasattr(artist_label.find_next_sibling(), 'a')):
                return dict({"titolo":0, "artista":"", "generi":[], "tracce":[]})
            else:
                artist_tag = artist_label.find_next_sibling().a
                if not hasattr(artist_tag, 'string'):
                    return dict({"titolo":0, "artista":"", "generi":[], "tracce":[]})
                else:
                    artist = artist_tag.string
                    # leggo classificazione per genere dell'album
                    genre_label = soup.body.find('th', string="Genere")
                    genre_tags = []
                    if genre_label != None:
                        genre_tags = genre_label.find_next_sibling().find_all('a')
                    for i in range( min(len(genre_tags) - 1, 3) ):
                        # salvo fino a un massimo di 3 generi per album
                        genres.append(genre_tags[i].string)

                    # salvo tracklist e numero tracce
                    track_par = getParagraphById(soup.body, "Tracce")
                    track_tags = filterTagNameSequence(['li', 'i'], track_par)
                    for t in track_tags:
                        try:
                            s = t.string
                            if '(' in s:
                                t_name = s[:s.index('(') - 1]
                            else:
                                t_name = s
                            if t_name not in tracks:
                                tracks.append(t_name);
                        except TypeError as e:
                            print "Error:", s, "is not a valid track."
                    print "succesfully retrieved page", url
                    print "read", len(tracks), "tracks\n"

    return dict({"titolo":album_title, "artista":artist, "generi":genres, "tracce":tracks})

def fetchLyrics(artista, traccia):

    lyrics = ""
    try:
        url = LWParse(artista, traccia)
        LyrReq = Request(url)
        response = urlopen(LyrReq)
        document = BeautifulSoup(response.read(size=-1), 'html.parser')
    except UnicodeEncodeError:
        print "Couldn't read url for", album["artista"] + ",", t
    except URLError:
        print "ERROR while fetching", url
        # errore nella rihiesta
    else:
        # cerco box contenente i testi
        lyricbox = document.find('div', { "class" : "lyricbox" })
        if not(lyricbox is None):
            # elimino elementi html residui:
            for br in lyricbox.find_all("br"):
                br.replace_with("\n")

            for lb in document.find_all('div', { "class" : "lyricsbreak" }):
                lb.replace_with("")

            lyrics = ""
            for riga in lyricbox.contents:
                tagpos = riga.find('<')
                while tagpos >= 0:
                    riga = removeTagPosition(riga, tagpos)
                    tagpos = riga.find('<')
                # criteri per
                if riga.find('(') < 0 and riga.find('[') < 0:
                    try:
                        lyrics += str(riga)
                    except UnicodeEncodeError:
                        lyrics += "/* In questa riga e' presente un carattere non valido"

    return lyrics



""""""""" PROGRAMMA """""""""

newalbum = { "titolo": "-1", "artista" : "", "generi" : [], "tracce" : []}

with cod.open(INPUT, 'r', 'utf-8-sig') as fin:
    for line in fin:

        tracklist = []

        # elimino il carattere di fine riga
        if line[len(line) - 1] == "\n":
            line = line[:len(line) - 1]
        if exists(line):
            album = newalbum.copy()
            album = fetchAlbumData(line)
            size = len(album["tracce"])
            if size > 0:
                tracce = album["tracce"]
                # calcolo uno "step" per prendere esattamente 'SONGS_TO_FETCH' canzoni
                step = size / SONGS_TO_FETCH
                # prendo una canzone ogni "step" canzoni
                if step > 1:
                    for i in range(size):
                        t = tracce.pop()
                        if i % step == 0:
                            tracklist.append(t)
                        # endif
                    # endfor
                # endif
                else:
                    for i in range(size):
                        t = tracce.pop()
                        tracklist.append(t)
            #^^elif album["titolo"] == 0:
                #^^ print line, "- album non trovato"
            #^^ else:
                #^^ print line, "- nessuna traccia trovata"

            """
            a questo punto, in tracklist[] sono salvate, per l'album in analisi,
            le tracce di cui devo cercare i testi

            """

            # scarico i testi da lyricswikia e li salvo su hard disk
            n_canzoni_scritte = 0
            info = {}

            for t in tracklist:

                lyrics = fetchLyrics(album["artista"], t)

                if lyrics != "":

                    filename = songFileName(album["artista"], t)
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    # formatto il percorso per ottenere un filename valido

                    for i in range(len(filepath)):
                        filepath_encoded = filepath.encode()
                        if filepath_encoded[i] == '/':
                            filepath_encoded = filepath_encoded[:i] + '-' + filepath_encoded[i+1:]
                    if filepath != filepath_encoded:
                        filepath = filepath_encoded.decode()

                    info["titolo"] = t
                    info["artista"] = album["artista"]
                    info["album"] = album["titolo"]
                    info["generi"] = album["generi"]
                    # creo file delle lyrics (se non esiste) e ci scrivo
                    try:
                        lyrfile = os.open(filepath, os.O_CREAT | os.O_WRONLY)
                    except OSError as err:
                        a = 0
                        #^^ print "Could not open file", filepath
                        #^^ print "Reason:", err.strerror, "\n"
                    else:
                        os.write(lyrfile, str(info) + "\n\n")    # riconvertibile con eval(s)
                        os.write(lyrfile, lyrics)
                        os.close(lyrfile)

                        n_canzoni_scritte += 1
                # endif
            # endfor
            #^^ print "successfully saved", n_canzoni_scritte, "tracks\n"
            #^^ print "Last album fetched:", line
        # endif if exists(line)
        #^^ else:
            #^^ print "Errore:", line
        # endelse
    # endfor

fin.close()
# endwith
