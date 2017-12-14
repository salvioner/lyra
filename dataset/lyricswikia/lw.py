# -*- coding: utf-8 -*-
from wikiparser.wp import urlFormat

def baseLWUrl():
    return "http://lyrics.wikia.com/wiki/"
    

def LWParse(artista, canzone):
    return baseLWUrl() + urlFormat(artista + ":" + canzone)
    
def removeTagPosition(s, pos):
    s_clean = s[:pos]
    i = pos
    while s[i] != '>' and i < len(s):
        i += 1
    i += 1
    s_clean += s[i:]
    return s_clean