#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import sys

class ManualError(Exception):
    def __init__(self, args):
        self.args = args
    def display(self):
        print(' '.join(self.args))

class LyricFinder:

    def search(self, query):
        return self._search_lyricswikia(query)
        # return self._search_azlyrics(query)

    def _search_lyricswikia(self, query):
        print("Searching lyrics.wikia.com")
        query = remove_multiple_spaces(query).lower()
        tokens1 = query.split()
        query = urlencode(query.lower())
        url = "http://lyrics.wikia.com/wiki/Special:Search?query={}".format(query)
        response = urllib.request.urlopen(url)
        extractor = BeautifulSoup(response.read(), "html.parser")
        divs = extractor.find_all("li", {'class' : 'result'})
        matches = []
        for div in divs:
            anchor = div.findAll('a')[0]
            title = anchor.text
            title = remove_multiple_spaces(remove_punct(title)).lower()
            tokens2 = title.split()
            link = anchor.attrs['href']
            dist = compute_jaccard(tokens1, tokens2)
            matches.append((title, link, dist))
        matches = sorted(matches, key = lambda x : x[2], reverse=True)
        if not matches:
            return ""

        url_full = matches[0][1]
        response = urllib.request.urlopen(url_full)
        extractor = BeautifulSoup(response.read(), "html.parser")
        div = extractor.find('div', {'class' : 'lyricbox'})
        return "" if not div else div.get_text('\n').strip()

    def _search_azlyrics(self, query):
        print("Searching azlyrics.com")
        links = self._get_links_azlyrics(query)
        print(links)
        if links:
            return self._get_links_azlyrics(links[0])
        else:
            return ''

    def _get_links_azlyrics(self, query):
        """
            Search the possible songs for this query.
            Returns the list of url for the song.
        """

        # first encode
        url = "http://search.azlyrics.com/search.php"
        query = urlencode(query.lower())
        url_query = "?q={}".format(query)
        url_search = url + url_query
        response = urllib.request.urlopen(url_search)
        extractor = BeautifulSoup(response.read(), "html.parser")

        anchors = []
        links = []

        # extract all the panels -> album, song, artist
        # since the search can give 3 type of div (panel)
        panels = extractor.find_all('div', {'class' : 'panel'})

        # now find the panel containing list of all the songs
        to_extract = ""
        for panel in panels:
            if re.search("song results", panel.text, re.IGNORECASE):
                to_extract = panel
                break

        # if nothing found
        if not to_extract:
            links = []
        else:
            table = to_extract.find_all("table", {'class' : 'table'})[0]
            rows = table.find_all('tr')
            anchors = [ row.find('td').find('a').get('href')  for row in rows ]

            # discard if the link/anchor is just a pagination link
            links = [ anchor for anchor in anchors if not url_query in anchor ]
        return links

    def _get_from_url_azlyric(self, url):
        response = urllib.request.urlopen(url)
        read_lyrics = response.read()
        soup = BeautifulSoup(read_lyrics, "html.parser")
        lyrics = soup.find_all("div", attrs={"class": None, "id": None})
        lyrics = [x.getText() for x in lyrics][0]
        return lyrics



def urlencode(text):
    """
        Url encode the text
    """
    q = {}
    encoded = ""
    if(text):
        q['q'] = text
        encoded = urllib.parse.urlencode(q)
        encoded = encoded[2::]
    return encoded

def compute_jaccard(tokens1, tokens2):
    union = set(tokens1).union(tokens2)
    # input(union)
    intersect = set(tokens1).intersection(tokens2)
    # input(intersect)
    return len(intersect)/len(union)

def remove_multiple_spaces(string):
    return re.sub(r'\s+', ' ', string)

def remove_punct(string):
    string = re.sub(r"[']+", '', string)
    return re.sub(r"[-:_!,/.()#?]+", ' ', string)


def main():
    args =  sys.argv
    # url = "http://search.azlyrics.com/search.php"
    query = ""
    lyric = ''
    lfinder = LyricFinder()
    if(len(args) > 1):
        query = ' '.join(args[1::])
        print("Searching...\nHave patience and be an awesome potato...")
        lyric = lfinder.search(query)
    if lyric:
        print(lyric)
    else:
        print("No songs found... -_-")

if __name__ == "__main__":
    main()

