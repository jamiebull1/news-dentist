"""
pliers.py
~~~~~~~~~
Tool used by news-dentist to extract the text of articles from the mouth of
Google News.

"""

import argparse
import itertools
import re
import shutil

from bs4 import BeautifulSoup
import requests


MIN_LENGTH = 20  # minimum line length in words

SEARCH_URL = 'https://www.google.com/search'

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3'
}

params = {
    'hl': 'en',
    'gl': 'uk',
    'tbm': 'nws',
}


def visible(element):
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
    elif re.match('\[if .*endif\]', str(element)):  # IE strings
        return False
    elif not element.strip():  # empty lines
        return False
    elif len(element.split()) < MIN_LENGTH:  # short lines, e.g. menu items
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
    return itertools.chain(regex_matches)


def fetch_results(links, completed):
    """
    Fetch the text from the article links and add the article to a list of
    links already visited.

    """
    batch = []
    for link in links:
        if link and link not in completed:
            res = requests.get(link[0], headers=headers)
            html = res.text
            soup = BeautifulSoup(html, 'lxml')
            texts = soup.find_all(text=True)
            visible_texts = filter(visible, texts)
            batch.extend(visible_texts)
            completed.append(link)
    return batch, completed


def linkify(query_txt):
    query_txt = query_txt.replace(' ', '_')
    query_txt = re.sub("[^a-zA-Z_]", "", query_txt)
    filename = "{}.txt".format(query_txt)
    return filename


def main(query, page_depth):
    """Main loop.
    """
    completed = []
    for page_depth in range(int(page_depth)):
        links = get_all_links(query, page_depth)
        # get links to try
        article_links = get_article_links(links)
        # try the links
        batch, completed = fetch_results(article_links, completed)
        # save the results
        with open('static/tmp/{}'.format(linkify(query)), 'w+') as f:
            f.writelines('\n'.join(l.strip() for l in batch))
    shutil.move('static/tmp/{}'.format(linkify(query)),
                'static/teeth/{}'.format(linkify(query)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Customisable extraction of text from the news.')
    parser.add_argument('-q', metavar='query', type=str,
                        help='search term')
    parser.add_argument('-d', metavar='page depth', type=int,
                        help='page depth (10 results per page)')

    args = parser.parse_args()

    main(args.q, args.d)
