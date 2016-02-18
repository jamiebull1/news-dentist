# -*- coding: utf-8 -*-
"""
toothcomb.py
~~~~~~~~~~~~
Toothcomb pulls out the most common words in a text, excluding a list of stop
words.

"""
from collections import Counter


STOPWORDS = ("a,able,about,across,after,all,almost,also,am,among,an,and,any,"
             "are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,"
             "does,either,else,ever,every,for,from,get,got,had,has,have,he,her"
             ",hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,"
             "like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,"
             "often,on,only,or,other,our,own,rather,said,say,says,she,should,"
             "since,so,some,than,that,the,their,them,then,there,these,they,"
             "this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,"
             "while,who,whom,why,will,with,would,yet,you,your".split(','))


def clean(w):
    """Remove some punctuation.
    """
    w = w.replace('.', '')
    w = w.replace(',', '')
    w = w.replace('"', '')
    return w


def main():
    with open('../glastonbury festival.txt', 'r') as f:
        text = f.readlines()
    c = Counter()
    for line in iter(text):
        c.update(clean(w) for w in line.split()
                 if clean(w).lower() not in STOPWORDS)

    print('Most common:')
    for word, count in c.most_common(1000):
        print('%s: %7d' % (word, count))

if __name__ == '__main__':
    main()
