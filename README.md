# Project Doom

Project Doom is a group of 4 of libraries used for in depth analysis of rap lyrics. Doom specifically focuses on rap verses; where other libraries analyze all lyrics of a song, Doom utilizes complex but rhobust filtering to extract verses and verses specific to indibidual artists.

Doom is written to be powerful enough for advanced programmers to use/tweak for their own research and simple enough for new comers/non-technical rap enthusiasts to utilize. By using container functions and detailing the start to finish, full scrape to vizualization process in full_proc.ipynb, I hope people from all expertise backgrounds can enjoy and learn something new. Please use/tweak full_proc.ipynb for a simple and high level guide to using the libraries, this readme goes into depth regarding each function and object within each library.

Doom is broken up into 4 libraries, each designed with a focused purpose addressing the full scrape to vizualization journey. Here are the libraries and their primary functionality/capabilties (click one to read the documentation):

#### [rap_scrpr](#rap_scrpr-guide)

This library scrapes from a [rap lyrics website](http://ohhla.com). For the most part, lyrics are organized in generally the same format with consistent labeling making the cleaning process simpler.

#### [rap_db](#rap_db-guide)
While not inherently necessary, this library is comprised of a group of functions to interact with a PostgreSQL database full of rap lyrics. It manages the entire data storage process, table creation, populating the database, and quereying it.

#### [rap_clean](#rap_clean-guide)
This is the most complex of the four libraries as it tackles the most challenging part of data retrieval. Per its name, it cleans and prunes lyrics stored in raw text data and extracts songs segments (intro, verse, chorus, outro, misc.). This project is dedicated to verses so there are additional filtering and objects/methods (word syllable extraction) focused on verses.

#### [rap_viz](#rap_viz-guide)
This library uses specialized artist, song, and verse objects created in rap_clean to vizualize lingustic meta data, verse syllable breakdowns, and verse sorting/rankings. The functions in rap_viz can also be used as a template for creating complex, more specific, or more dynamic vizualizations based on user preference.

#### rap_mach
This library is undergoing development. You may be able to guess by its name what it might do.

## Installing and Library Dependencies

### Installing Doom
```
pip install git+git://github.com/m4n0b0dy/doom
NEWCOMERS - This does not install all the other libraries necessary to run Doom
```

### Library Dependencies
I'm not shy about using other libraries, and given the different goals of each library, they use a ton of external functions. Here are the dependenceis broken up by library; once a library has been listed, it isn't re-listed when imported again in a different Doom library. For your own sanity, I would HIGHLY recommend using Anaconda and installing all the unincluded ones individually.

#### rap_scrpr
```
import json
import re
from bs4 import BeautifulSoup
import urllib
import time
```
#### rap_db
```
import psycopg2 as pg2
import psycopg2.extras
import pickle as pic
from os import listdir
from os import path
from os.path import isfile, join
```
#### rap_clean
```
from nltk.corpus import stopwords
from nltk.stem import *
from difflib import SequenceMatcher
from difflib import get_close_matches
from nltk.corpus import cmudict
import pyphen
```
#### rap_viz
```
from statistics import mean, median
import plotly.offline as offline
import plotly.figure_factory as ff
import plotly.graph_objs as go
from collections import Counter
from random import shuffle
from IPython.core.display import display, HTML
from copy import deepcopy
```

## Doom Library Function and Object Guides

#### rap_scrpr guide
```
pull_links(page_link, app, sng_scr=False)
```
This sub function pulls a list of links to feed into scraper. It may run twice if artist page is in certain format (auto detects)
page_link: link to page pulling links from
app: specialized character appending for certain artist pages
sng_scr = False: indicating if it's one of those special artists
returns list of song links
```
song_links(page_link, slept=.1)
```
This sub function takes in artist/album links and uses pull_links to find song links (more of a wrapper function)
page_link: artist page link
slept = .1: rest scraper between scrape to not overload host server
returns list of song links from artist input
```
song_scrape(links, slept=1)
```
This function scrapes a list of SONG LINKS (must be song links)
links: song links
slept = 1: sleep between song scrapes (without rest subject to 403 errors)
returns list of raw song texts
```
raw_clean(song_texts)
```
This very simple cleaning function loads in raw text and identifies artist, album, song from data included in ohhla. If it can't id it, labels text "raw"
song_texts: list of string song texts
returns dictionary of cleaned song texts (artist:album:title:lyrics)
```
scrape_multi_artists(conn, artist_list)
```
This function uses pull_link_from_art to pull each link for each artist from DB. Then it iterates over artist links and scrapes/applies above functions to each artist and saves them to individual JSON files
conn: postgresql connection object
artist_list: list of artist names that map to DB records
returns list of strings that are names of new JSON files
#### rap_db guide
Pretty much all functions in this library interact with our database of lyrics. Some are for data management/saving. Given their jobs, they don't return anything unless stating otherwise
```
create_music_tables(conn, bypass = False)
```
This function eraeses and creates 4 tables (base_artist, artists, albums, songs) that will hold our data
conn: postgresql connector object
bypass = False: a boolean to bypass the warning signal (warning cause you'd be erasing everything!)
```
add_base(conn, base_art_name)
```
This function adds a special table to record which JSON file contributed what. It's not used later but helpful to refer back to ohhla
conn: postgresql connector object
base_art_name: JSON file name - '.json'
```
add_songs(conn, base_art_name, art_name, art)
```
This function adds songs to the DB! It uses the dictionary format we saved the JSON files in via rap_scrpr (artist:album:song:lyrics)
conn: postgresql connector object
base_art_name: json file name - '.json'
art_name: string of artist name
art: artist dictionary saved into JSON file
```
percise_pull(conn, art, alb=False, song=False)
```
This is a depricated but faster way to pull a song. It can pull all of an artists works, certain albums, or certain songs. However, it can only do one artist at a time
conn: postgresql connector object
art: string artist name
alb: string album name
song: string song name
returns dictionary consisting of this format (artist:artist:song:lyrics)
```
update_art_dic(art_dic, query, base_artist, use_ind_artists)

```
This function assists the adv_pull function by continually updating a dictionary that consists of an artists work. It outputs the same dictionary that inputs to keep updating it as more and more song sare pulled
art_dic: a dictionary containing the full query information for an individual artist, always organized (artist:album:song:lyrics)
query: this is a dictionary comprised of the returns of a DB query
base_artist: this is a string of the USER INPUTTED artist name. Otherwise it would use the names in the DB (it gets those from ohhla)
use_ind_artists: a boolean that is typically false (usually use user input artist name). If it is true, the art_dic will be organized by the names in the DB which uses the ohhala true artist name which can contian features, typos, etc.
returns continually updating dictionary for singular artist
```
adv_pull(conn, artist_list = [''], album_list = [''], song_list = [''], use_ind_artists=False)
```
This function is more advanced than percise_pull. It can handle multiple artists, multiple albums, or multiple songs. As a result it has much simpler inputs but is slower.
conn: postgresql connector object
artist_list: list strings of artist names
album_list: list of strings of album names
song_list: list of strings of song names
use_ind_artists: boolean that is rarely used, use case described above
returns a dictonary of artist song info in this format (multiple artists:respective albums:respective songs:respective lyrics)
```
pull_link_from_art(conn, artist_name)
```
This pulls the ohhla link from a special table using an artist name. Not vital but makes it really easy to scrape.
conn: postgresql connector object
artist_name: string containing artist name matching db (case doesn't matter)
returns the ohhla link to scrape
```
def bulk_load(conn, new_eds = [])
```
This is a wrapper function that uses the above functions to load in new JSON files into DB easily (DOES NOT RECREATE/ERASE TABLES).
conn: postgresql connector object
new_eds: list of strings of JSON files
```
art_save(arts)
```
This has nothing to do with databases but is for data management. Once an artist object is created, you can save it as a pickle file to a folder with this function. Create artist objects involves a lot of cleaning and labeling so it greatly speeds process. Also elminates need for database for high level artist analysis.
arts: list of artist objects
```
art_load(nms = set())
```
This loads those pickle files for quick and easy access. With no arguments, it loads all artist objects in folder.
nms = set(): list of strings referring to artist object names to load in (just the name, don't need to include .pkl)
#### rap_clean guide
This is by far the most complex of the libraries. I wrote this library and it's guide in this order functions that support objects, objects (with methods), functions that load/create/populate objects. Because data cleaning is such an important part of data science, there are a lot of choices I made (reflected in the function arguments) in construction of each verse object. This is based on what I saw as the most efficient and accurate way to filter out non-verses. However, some may want to revisit my cleaning methadology, make improvements and filter differently: every function and object is equippied for revision.
```
#quick way to check if it's a true verse, 20 charcaters and at least 12 unique words
check_verse(text, nec_len = 20, nec_uniq = 12)
#this specialized function pulls out verses that are by specific artist (not features) and don't match any other verse to 50%
find_uniq_art_vers(ar, all_ver_lst, ratio_check=.5)
#simple and fast recursive flatten function to flatten any object
flatten(container)
#used to hold and breakdown words
#most complex of all objects/functions
class word(self, text):
    #deconstruct word into vowel sounds and sylbl sounds and match them
    word.my_split(self, text_to_split, vowel_config, ap='', ap_num=False)
    #this is used for known special splitting for 0 or 1 sylbl sounds using unique vowel combos
    word.spec_split(self, cur_vowel_config, regex_end, ap_syls)
    #this function matches vowel sylbls to word sylbls for colorizing
    word.sylbl_match(self)
class text_segment(self, typ, label, start, end)
    text_segment.gen_content(self, raw_text, next_start)
class verse(text_segment):
    #simple way of getting verse as lines, words, unique words and a sylbl dic for low storage
    verse.split_to_words(self)
    verse.split_on_stem(self)
    verse.run_all_split(self)
class song(self, raw_text, name, artist):
    #go through regex and compile dict and set of locaitons of each pattern match
    song.assign_extras(self)
    #this removes the full captured text of any of the regex formations utilized above and recalculates all the new positions
    song.remove_and_reass(self, rems = [])
    #using our ordered list of regex matches from before, create a song out of the segments it's comprised of
    song.create_song_as_seg(self)
#simple function to pull song info
flatten_songs(song_list)
#album is a wrapper for holding songs, and verses, don't need it to hold song_segments but it can
class album(self, artist, name, songs)
#aritst is similar but holds albums, songs and verses
class artist(self, name, albums)
#finally a function to build all this stuff
construct_albums(albs_dic, artist_nm)
#temp album searches
construct_artists(conn, art_list = [''], alb_list = [''], sng_list = [''], use_ind_artists=False)
```
#### rap_viz guide
```
gen_plot(typ, traces, arts, b)
unique_words_hist(artist_obj_list, all_feat_artist=False, song_or_verse='verse', b=.01)
#my favorite funciton of all time tbh
unique_verses_bar(artist_obj_list, all_feat_artist=False, verse_count = 10)
#nice! By album as well
unique_count_to_length(artist_obj_list, all_feat_artist=False, by_alb=False)
#searches an artists work and pulls a song and verse number
verse_search(artist_obj, song_name, verse_number=0)
#mainly a container for words and meta word data
class line(self, word_objs)
#used in both vizualizing verses and optoing sylbl matching
class verse_graph(self, verse_obj, artist_name, song_name)    
    verse_graph.opto_matches(self, pop=False, exc_line=False, opto_type='exact')
    #create a color dic corresponding to used vowel sounds
    verse_graph.colorize_vowels(self, match_type='near')
    #use html to plot verse and save html version
    verse_graph.graph_colored_verse(self)
```
