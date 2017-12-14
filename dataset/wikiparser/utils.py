from wikiparser import wp

# more messages are to be added with relative non-existing-page title strings
messages = { 'it':  '(la pagina non esiste)'}

def endsWith(s, end):
    end_l = len(end) 
    s_l = len(s)
    i = s_l - end_l
    return s[i:] == end

def exists(page_title):
    lang_i = wp.defaultLang
    if endsWith(page_title, messages[lang_i]):
        return False
    else:
        return True