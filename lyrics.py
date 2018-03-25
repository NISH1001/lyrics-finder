#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import sys

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


class ManualError(Exception):
    def __init__(self, args):
        self.args = args
    def display(self):
        print(' '.join(self.args))

def search(url, query):
    """
        Searches the possible songs for this query.
        Returns the list of url for the song
    """

    # first encode
    query = urlencode(query.lower())
    url_query = "?q={}".format(query)
    url_search = url + url_query
    response = urllib.request.urlopen(url_search)
    extractor = BeautifulSoup(response.read(), "html.parser")
    anchors = []
    links = []
    try:
        table = extractor.find_all("table", {'class' : 'table'})[0]
        rows = table.find_all('tr')
        anchors = [ row.find('td').find('a').get('href')  for row in rows ]

        # discard if the link/anchor is just a pagination link
        links = [ anchor for anchor in anchors if not url_query in anchor ]
        if len(links) < 1:
            raise ManualError("no songs...")
    except ManualError as merr:
        merr.display()
        link = []
    return links

def search2(url, query):
    """
        Search the possible songs for this query.
        Returns the list of url for the song.
    """

    # first encode
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


def lyrics_full(url):
    response = urllib.request.urlopen(url)
    read_lyrics = response.read()
    soup = BeautifulSoup(read_lyrics, "html.parser")
    lyrics = soup.find_all("div", attrs={"class": None, "id": None})
    lyrics = [x.getText() for x in lyrics][0]
    return lyrics

def select_song(links, topn=5):
    inp = input("Select song ")
    return int(inp)

def main():
    args =  sys.argv
    url = "http://search.azlyrics.com/search.php"
    links = []
    query = ""

    if(len(args) > 1):
        query = ' '.join(args[1::])
        print("Searching...\nHave patience and be an awesome potato...")
        links = search2(url, query)

    if links:
        print(links)
        s =select_song(links, 4)
        lyrics = lyrics_full(links[0])
        print(lyrics)
    else:
        print("No songs found... -_-")

if __name__ == "__main__":
    main()

