# -*- coding: utf-8 -*-
"""
toothcomb.py
~~~~~~~~~~~~
Toothcomb pulls out the most common words in a text, excluding a list of stop
words.

"""
from collections import Counter
import os
import string


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(THIS_DIR, "static")

STOPWORDS = ("a,able,about,across,after,all,almost,also,am,among,an,and,any,"
             "are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,"
             "does,either,else,ever,every,for,from,get,got,had,has,have,he,her"
             ",hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,"
             "like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,"
             "often,on,only,or,other,our,own,rather,said,say,says,she,should,"
             "since,so,some,than,that,the,their,them,then,there,these,they,"
             "this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,"
             "while,who,whom,why,will,with,would,yet,you,your,--,—,-,"
             "–,".split(','))

def clean(w):
    """Strip whitespace and punctuation.
    """
    w = w.strip(string.punctuation + string.whitespace)

    return w


class Text():

    def __init__(self, path):
        filepath = os.path.join(STATIC_DIR, 'teeth', path)
        with open(filepath, 'r', encoding='utf8') as f:
            text = f.readlines()
        c = Counter()
        for line in iter(text):
            c.update(clean(w) for w in line.split()
                     if clean(w).lower() not in STOPWORDS)
        self.c = c

    def most_common(self, n=10):
        mc = self.c.most_common(n)
        return self.c.most_common(n)
