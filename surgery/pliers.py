# -*- coding: utf-8 -*-
"""
pliers.py
~~~~~~~~~
Tool used by news-dentist to extract the text of articles from the mouth of
Google News.

"""

from concurrent import futures
import argparse
import os
import re
import time
from functools import partial

from bs4 import BeautifulSoup
import requests


SEARCH_URL = 'https://www.google.com/search'
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(THIS_DIR, "static")

MAX_WORKERS = 20
MIN_LENGTH = 20

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3'
}

params = {
    'hl': 'en',
    'gl': 'uk',
    'tbm': 'nws',
}


def visible(element, minlength):
    """Filter out lines which are not part of the main text.
    """
    if element.parent.name in [
        'style',
        'script',
        '[document]',
        'head',
        'title',
    ]:
        return False
    elif '<' in str(element) and '>' in str(element):  # HTML tags
        return False
    elif '//' in str(element):  # comment tags
        return False
    elif '{*' in str(element):  # comment tags
        return False
    elif re.match('\[if .*endif\]', str(element)):  # IE strings
        return False
    elif not element.strip():  # empty lines
        return False
    elif len(element.split()) < int(minlength):  # short lines, e.g. menu items
        return False
    elif '©' in element:  # copyright lines
        return False
    elif 'CloudFlare' in element:  # DDOS protection service
        return False
    return True


def get_all_links(query, page_depth):
    """Get article links for the query at the given page depth.
    """
    params['q'] = query
    params['start'] = page_depth * 10
    res = requests.get(SEARCH_URL, params=params, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    return soup.find_all('a')


def get_article_links(links):
    """Get links which match the format used in Google Search results.
    """
    regex_matches = [
        re.findall(r'/url\?q=(http.*)&sa=U', link['href'])
        for link in links]
    return list(m[0] for m in regex_matches if m)


def fetch_results(links, stopwords, minlength):
    """
    Fetch the text from the article links and add the article to a list of
    links already visited.

    """
    batch = []
    to_fetch = [link for link in links if link]
    if not to_fetch:
        return batch
    workers = min(MAX_WORKERS, len(to_fetch))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(partial(extract,
                                   stopwords=stopwords,
                                   minlength=minlength), to_fetch)
    for r in res:
        batch.extend(list(r))
    return batch


def extract(link, stopwords=None, minlength=None):
    """Fetch and process a link, retaining text which appears to be body text.
    """
    try:
        res = requests.get(link, headers=headers, timeout=5)
    except Exception as e:
        print("Exception", e)
        return []
    html = str(res.text)
    soup = BeautifulSoup(html, 'lxml')
    texts = soup.find_all(text=True)
    lines = list(filter(partial(visible, minlength=minlength), texts))
    if lines:
        print('Received %i lines from: %s' % (len(lines), link))
    if any(word in html for word in stopwords):
        return []
    return lines


def linkify(query_txt, timestr):
    """Make a query into a safe filename with timestamp.
    """
    query_txt = query_txt.replace(' ', '_')
    query_txt = re.sub("[^a-zA-Z_]", "", query_txt)
    timestr = re.sub(r"[/:-]", "", timestr)
    filename = "{}_{}.txt".format(query_txt, timestr)
    return filename


def main(query, page_depth=1, file_name='', stopwords=None, minlength=''):
    """Main loop.
    """
    if minlength == '':
        minlength = MIN_LENGTH
    with open(os.path.join(
            STATIC_DIR, 'teeth/{}'.format(file_name)), 'w') as tmp_f:
        tmp_f.write('Waiting for results.')
    batch = []
    for page_depth in range(int(page_depth)):
        links = get_all_links(query, page_depth)
        # get unique links to try
        article_links = set(get_article_links(links))
        # try the links
        batch.extend(fetch_results(article_links, stopwords, minlength))
    # save the results
    print(os.path.join(STATIC_DIR, 'teeth/{}'.format(file_name)))
    with open(os.path.join(STATIC_DIR, 'teeth/{}'.format(file_name)), 'w',
              encoding='utf8') as f:
        f.writelines('\n'.join(l.strip() for l in batch))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Customisable extraction of text from the news.')
    parser.add_argument('-q', metavar='query', type=str,
                        help='search term')
    parser.add_argument('-d', metavar='page depth', type=int,
                        help='page depth (10 results per page)')

    args = parser.parse_args()

    main(args.q, args.d)
