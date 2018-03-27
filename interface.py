from tkinter import *
from tkinter.messagebox import showinfo
import re
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse

url = "http://search.azlyrics.com/search.php"
song_and_name = []

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

def search2(query):
    """
        Search the possible songs for this query.
        Returns the list of url for the song.
    """

    query = urlencode(query.lower())
    url_query = "?q={}".format(query)
    url_search = url + url_query
    response = urllib.request.urlopen(url_search)
    extractor = BeautifulSoup(response.read(), "html.parser")

    anchors = []
    links = []
    global song_and_name
    song_and_name = []

    panels = extractor.find_all('div', {'class' : 'panel'})

    to_extract = ""
    for panel in panels:
        if re.search("song results", panel.text, re.IGNORECASE):
            to_extract = panel
            break

    if not to_extract:
        links = []
        song_and_name = []

    else:
        table = to_extract.find_all("table", {'class' : 'table'})[0]
        rows = table.find_all('tr')
        for row in rows:
            pair = []
            for elem in row.find('td'):
                if "<b>" in str(elem):
                    pair.append(elem.getText())
                if "<small>" in str(elem):
                    pair.insert(3,elem.getText())
                if "href" in str(elem):
                    pair.insert(0,elem.get('href'))
            song_and_name.append(pair)
            
        song_and_name = [ anchor for anchor in song_and_name if not url_query in anchor[0] ]

def lyrics_full(url):
    response = urllib.request.urlopen(url)
    read_lyrics = response.read()
    soup = BeautifulSoup(read_lyrics, "html.parser")
    lyrics = soup.find_all("div", attrs={"class": None, "id": None})
    lyrics = [x.getText() for x in lyrics][0]
    return lyrics

def get_lyrics(index):
    url = song_and_name[index][0]
    return [song_and_name[index][1] + " - " + song_and_name[index][2], lyrics_full(url)]

class Application(Frame):
    """
        Interface for the user
    """

    def __init__(self, master):
        """
            Initializes the Window
        """

        self.master = master
        self.frame = Frame(self.master)
        self.frame.winfo_toplevel().title("Lyric finder")
        self.label_info = Label(self.frame, text="Type the keyword")
        self.label_info.grid(row=0,column=0,padx=10,pady=10)
        self.entry_text = Entry(self.frame,width=30)
        self.entry_text.grid(row=0,column=1,padx=10,pady=10)
        self.button_bonus = Button(self.frame, width=20, text="Get songs",
        command=lambda: [f for f in [search2(self.entry_text.get()), self.update_ListBox()]])
        self.button_bonus.grid(row=0,column=2,padx=10,pady=10)

        self.selectsong = Listbox(self.frame,selectmode="simple")
        self.selectsong.config(width=50)
        self.selectsong.grid(row=1,column=0,padx=10,pady=10,rowspan=2,columnspan=2)
        self.lyrics_label = Label(self.frame, text="")
        self.lyrics_label.config(width=50,wraplength=250)
        self.lyrics_label.grid(row=1,column=2,padx=10,pady=10,rowspan=2,columnspan=2)

        self.button_showinfo = Button(self.frame, width=20, text="Show Song",
        command=self.new_window, state="disabled")
        self.button_showinfo.grid(row=0,column=3,padx=10,pady=10)

        self.update_lyricsPreview()
        self.frame.pack()

    def update_ListBox(self):
        self.selectsong.delete(0,END)
        for x in reversed(song_and_name):
            self.selectsong.insert(0,x[1] + "-" + x[2])

    def update_lyricsPreview(self):
        if self.selectsong.curselection():
            self.button_showinfo.config(state="normal")
            self.lyrics_label.configure(text=song_and_name[self.selectsong.curselection()[0]][3])
        else:
            self.button_showinfo.config(state="disabled")
            self.lyrics_label.configure(text="")
        self.frame.after(1000, self.update_lyricsPreview)

    def new_window(self):
        song, lyrics = get_lyrics(self.selectsong.curselection()[0])
        self.newWindow = Toplevel(self.master)
        self.app = LyricWindow(self.newWindow, song, lyrics)

class LyricWindow:
    """
        Window where lyrics will be displayed
    """

    def __init__(self, master, song, lyrics):
        """
            Initializes new Window
        """

        self.master = master
        self.frame = Frame(self.master)
        self.frame.winfo_toplevel().title(song)
        self.canvas = Canvas(self.frame)
        self.scrollbary = Scrollbar(self.frame, command=self.canvas.yview,orient="vertical")
        self.scrollbary.pack(side=RIGHT, fill=Y)
        self.lyrics_output = Label(self.canvas, text = lyrics)
        self.lyrics_output.pack(padx=10,pady=10)
        self.lyrics_output.config(wraplength=0)

        self.canvas.create_window((0,0), window=self.lyrics_output, anchor='nw')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=self.scrollbary.set)
        self.canvas.pack(fill='both', expand=True, side=LEFT)

        self.frame.pack()

    def close_windows(self):
        """
            Destroys current window
        """
        self.master.destroy()

def main():
    root = Tk()

    app = Application(root)

    root.mainloop()

if __name__ == "__main__":
    main()
