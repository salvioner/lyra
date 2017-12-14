# -*- coding: utf-8 -*-

def getFetchedTitle(s):
    end = (len(s)-2)
    if s[end:] == ",\n":
        return s[0:end]
    else:
        # ultima parola dell'elenco
        return s

def filterTagNameSequence(tags, coll):
    coll_ = []  # istanzio una collection vuota
    for el in coll:
        # filtro una lista di elementi che contengono il tag:
        t = el(tags[0])
        # se la lista non è vuota, aggiungo tutti gli elementi alla nuova collection
        for el_ in t:
            coll_.append(el_)
    if len(tags) > 1:
        return filterTagNameSequence(tags[1:], coll_)
    else:
        # restituisco la nuova lista di tag
        return coll_

def getParagraphById(body, title_span_id):
    title_span = body.find(id=title_span_id)
    if title_span == None:
        return []
    title = title_span.parent
    nextTitle = title.find_next_sibling(title.name)
    # look for the string that matches title and return all the html
    # until nextTitle is found.
    paragraph = [title]
    for el in title.find_next_siblings():
        if el == nextTitle:
            break
        else:
            paragraph.append(el)
    return paragraph


def songFileName(artista, traccia):
    return artista + "_" + traccia + ".lyr"
