# -*- coding: utf-8 -*-
"""
pliers.py
~~~~~~~~~
Tool used by news-dentist to extract the text of articles from the mouth of
Google News. We use a regular user-agent string for searches on Google News,
followed by downloading text for analysis using the Google News user-agent
string.

"""

from concurrent import futures
from functools import partial
import os
import re

from bs4 import BeautifulSoup
import requests

from surgery.config import googler


SEARCH_URL = 'https://www.google.com/search'

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(THIS_DIR, "static")

MAX_WORKERS = 20
MIN_LENGTH = 20

headers = {'search': {
                      'User-Agent':
                      'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3'
                      },
           'download': {'User-Agent': 'Googlebot-News'}}

params = {
    'hl': 'en-GB', # search in English
    'gl': 'uk',    # search UK
    'tbm': 'nws',  # search news sites
    'pws': 0,      # don't personalise searches
    'gbv': 1,      # disable javascript
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
#    set_abuse_prevention_cookie(GOOGLE_ABUSE_PREVENTION)
    params['q'] = query
    params['num'] = page_depth * 10
    res = googler.session.get(
        SEARCH_URL, params=params, headers=headers.get('search'))
    html = res.content
    print("STATUS CODE")
    print(res.status_code)
    print("REQUEST HEADERS")
    print(res.request.headers)
    print("RESPONSE HEADERS")
    print(res.headers)
    print("COOKIES")
    print(googler.session.cookies)

    soup = BeautifulSoup(html, 'html.parser')
    if res.status_code == 503:
        return {'captcha': res.url}
    else:
        return soup.find_all('a')



def get_article_links(links):
    """Get links which match the format used in Google Search results.
    """
    regex_matches = [
        re.findall(r'/url\?q=(http.*)&sa=U', link['href'])
        for link in links]
    return list(m[0] for m in regex_matches if m)


def fetch_results(links, minlength):
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
                                   minlength=minlength), to_fetch)
    for r in res:
        batch.extend(list(r))
    return batch


def extract(link, minlength=None):
    """Fetch and process a link, retaining text which appears to be body text.
    """
    try:
        res = requests.get(link, headers=headers.get('download'), timeout=5)
    except Exception as e:
        print("Exception", e)
        return []
    html = str(res.text)
    soup = BeautifulSoup(html, 'lxml')
    texts = soup.find_all(text=True)
    lines = list(filter(partial(visible, minlength=minlength), texts))
    if lines:
        print('Received %i lines from: %s' % (len(lines), link))
    return lines


def linkify(query_txt, timestr):
    """Make a query into a safe filename with timestamp.
    """
    query_txt = query_txt.replace(' ', '_')
    query_txt = re.sub("[^a-zA-Z0-9_]", "", query_txt)
    timestr = re.sub(r"[/:-]", "", timestr)
    filename = "{}_{}.txt".format(query_txt, timestr)
    return filename


def set_cookie(cookie):
    """
    Set a GOOGLE_ABUSE_EXEMPTION cookie retrieved after manually completing a
    CAPTCHA challenge.
    
    """
    googler.session.cookies['GOOGLE_ABUSE_EXEMPTION'] = cookie.strip()


def main(query, page_depth=1, file_name='', minlength='', cookie=''):
    if page_depth == '':
        page_depth = 1
        
    if minlength == '':
        minlength = MIN_LENGTH
        
    if cookie:
        set_cookie(cookie)
    # write a dummy file
    with open(os.path.join(
            STATIC_DIR, 'teeth/{}'.format(file_name)), 'w') as tmp_f:
        tmp_f.write('Waiting for results.')
    # fetch links from Google
    links = get_all_links(query, int(page_depth))    
    if 'captcha' in links:
        return links
    # get unique links to try
    article_links = set(get_article_links(links))
    # try the links
    batch = fetch_results(article_links, minlength)
    # save the results
    with open(os.path.join(STATIC_DIR, 'teeth/{}'.format(file_name)), 'w',
              encoding='utf8') as f:
        f.writelines('\n'.join(l.strip() for l in batch))
