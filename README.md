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
##### This sub function pulls a list of links to feed into scraper. It may run twice if artist page is in certain format (auto detects)\
page_link: link to page pulling links from\
app: specialized character appending for certain artist pages\
sng_scr = False: indicating if it's one of those special artists\
returns: list of song links
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
This is by far the most complex of the libraries. I wrote this library and it's guide in this order -functions that support objects, objects (with methods), functions that load/create/populate objects-. Because data cleaning is such an important part of data science, there are a lot of choices I made (reflected in the function argument line) in construction of each verse object. This is based on what I saw as the most efficient and accurate way to filter out non-verses. However, some may want to revisit my cleaning methadology, make improvements and filter differently: every function and object is equippied for revision.
```
check_verse(text, nec_len = 20, nec_uniq = 12)
```
This checks if a long string of lyrics is really a verese. By default, it must be at least 20 char long and have 12 unique words
text: text lyrics as string
nec_len = 20: minimum character count
nec_uniq = 12: min unique word count
returns true or false based on check
```
find_uniq_art_vers(ar, all_ver_lst, ratio_check=.5)
```
Similarly, this checks if a long string is really by the target artist (not a features' verse) and shouldn't be classified as a chorus. By default, any text lyrics with 50% similarity are considered to be choruses (as they are repeated)
ar: artist name, used to check if actually by artist
all_ver_lst: this is a set of all the verses we will check. They are all loaded in at once as they need to be compared to each other
ratio_check = .5: this is the minimum similarity that will trigger a False for a verse. If they have more than 50% similarity they aren't verses
returns a list of true, artist unique verses (later used as sttribute)
```
flatten(container)
```
This simply takes a list, tuple, set, containr that contains other containers and flattens every element until it is all in one container
container: list of lits, tuple of tuples, list of lists of lists, etc.
returns flattened container
```
class word(self, text):
```
This object is used to hold and analyze individual words. It can segment a word into vowel sounds and syllable sounds even when misspelled. It has only two methods but many attributes. __init__ runs complex functionality, but the overall goal is to match the count of vowel sounds to syllables for any given word
text: word as string

Here are its attributes
```
word.text #the true word in string format
word.found_text #the closest word in CMU dict in string format (same as word.text if in dict)
word.all_found_words #a list of 5 words that are closest to word.txt
word.vowel_sounds #the primary guess at the correct number of/vowel sounds of a word
word.sylbl_sounds #the primary guess at the correct number of/syllable soudns of a word
word.same_vowel_sounds #a list of possible vowel breakdowns that have the same length as word.sylbl_sounds
word.matches #a list of tuples in the format (syllable:vowel sound)
```
```
word.my_split(self, text_to_split, vowel_config, ap='', ap_num=False)
```
This is my custom splitting algorithim when traditional vowel and syllable breakdowns don't match in length (for colorization)
text_to_split: text that will run through algorithim
vowel_config: a vowel configuration used to match multiple syllable breakdowns
ap, ap_num: only used by other functions, no need to edit (used in special pronucniation edge cases)
```
spec_split(self, cur_vowel_config, regex_end, ap_syls)
```
This is used for special vowel combinations that product 1 or 0 vowel sounds "tion", "eve". These are matched on regex with an associated vowel count
cur_vowel_config: vowel breakdown of the word (fed into my_split)
regex_end: the regex used to find the special character combo
ap_syls: the number of vowel sounds that match is responsible for
```
word.sylbl_match(self)
```
This is a simple method that combines vowel sounds with syllable soudns. If no match is found, set attribute to unknown.
```
class text_segment(self, typ, label, start, end)
```
This is a basic text segment object. It can store where the text segment is for removal or analyses
typ: the type of text segment (held within regex class attribute of song)
label: the contents within the bracket, parenthesees, curly bracets, etc. type
start: the position in the text where the label starts
end: the position in the text where the content ends
```    
text_segment.gen_content(self, raw_text, next_start)
```
This method extracts content from the text segment based on where the next text segment starts and contents of the current text segemnt
raw_text: the entire song as a text string
next_start: where the next text segment begins
self.content = the content of that segment
```
class verse(text_segment):
```
Uses inheritance from text segment. Everything is stored the same, when class song creates verse dictionaries, it utilizes the two checks described above
```
verse.split_to_words(self)
```
This splits the text segment into lines, and those lines into words. It then turns each word as a string into a word object (and runs word object methods). It stores these word objects in a dictionary (for speed and memory managment) and otehr attributes for later use
verse.all_words_by_line: list of words as strings, line by line
verse.all_words: a list of strings, each string is a word in verse
verse.unique_words: a set of strings, each string is a unique word in verse
self.word_objs: a dictionary in this format (word as string: word as word object)
```
class song(self, raw_text, name, artist):
```
This takes in raw lyrics as text and creates segments out of them. Segments are text segments (with different types) or verses. Each verse goes through deeper analysis.
Attribtes
CLASS.regex_commands: this is a large dictionary of text segment types to regex commands that can extract them. It is a class attribute as it will always be used
song.raw_text: lyrics as string
song.name: name of song
song.artist: name of artist
```
song.assign_extras(self)
```
This goes through regex dictionary and finds every segment it can. It marks where it starts, where it ends and its content. It also does a quick check override for verses and saves special seg types that will eventually be created as text_segments
self.extras: a dictionary of every single text segment type and their matching start, end, content. Can be used for removal, text_segment creation, etc.
self.extra_segs: a list of extras values that will be used to create the song as a segment, includes ['verse', 'chorus', 'intro', 'outro', '[]']
```
song.remove_and_reass(self, rems = [])
```
This goes through a list of types that we want to have removed from the song, removes them and their content and recalculates the extras.
rems: a list of types (regex dictionary keys) we want removed
```
song.create_song_as_seg(self)
```
This goes through self.extra_segs and creates each one into a text segment. It also creates/checks text segments if they should be verses and makes a verse object instead. It populates song.segments.
Attributes
song.segmets: a list of text_segment objects and verses that make up a song
song.verses: a list of just the verses
song.uniq_art_verses: a list of verses that also passed the unique test listed earlier
```
flatten_songs(song_list)
```
This flattens a list of songs into one list to simplify making album and artist container
song_list: list of list of song objects
returns list of song objects
```
class album(self, artist, name, songs)
```
This is a container object that holds song objects.
album.artist: artist name as string
album.name: album name as string
album.songs: a list of song objects
album.verses: a list of verse objects
album.uniq_art_verses: a list of vereses that also passed unique test
```
class artist(self, name, albums)
```
This is another contianer at the artist level. It has similar attributes to album but also contains albums. This overlap of information allows for more specific searching. Since objects are already created, it doesn't vastly increase time by copying them again (does increase total memory spcae)
artist.name: artist name as string
artist.albums: a list of album objects
artist.songs: a list of song objects
artist.verses: a list of verse objects
artist.uniq_art_verses: a list of vereses that also passed unique test
```
construct_albums(albs_dic, artist_nm)
```
This function builds out artist, album, song, text_segments, verses, word objects from a database pull. It takes in the artists name, and a dictionary in the format (album:song:lyrics) and makes appropirate objects.
albs_dic: a dictionary of albums to songs to lyrics, formatted in (album:song:lyrics)
artist_nm: the artist we are creating's name as a string
```
construct_artists(conn, art_list = [''], alb_list = [''], sng_list = [''], use_ind_artists=False)
```
This function uses adv_pull from rap_db to pull an artists work from the database. It can search for multiple artists filtered by albums or songs.
conn: a postgresql connection object
art_list: a list of artist names as strings to pull/filter with from DB
alb_list: a list of album names as strings to pull/filter with from DB
sng_list: a list of song names as strings to pull/filter with from DB
use_ind_artist: a boolean that should be set as false. Only set to true when using the artist names in the database over the artist name used in select statement
returns a dictionary in the format (artist name as string:artist object (containing all attributes listed above))
#### rap_viz guide
All graphical vizualizations are based on the amazing and easy to use Plotly library; since they are similar, their functional arguments are also similar. The syllable colorziation vizualization was written by me. They don't return anything as they plot the vizualization in the notebook. I plan on recreating these functions with the ability to order/size according to multiple different metrics for later vizualization/exploration
```
gen_plot(typ, traces, arts, b)
```
This supports the unique_words_hist which vizualizes distributions by verse or by song of the (total unique words)/(all words) ratio.
typ: verse or song as string
traces: these are plotly items that hold information about each datum point/bar
arts: the artists used in the vizuailization
b: the bin size of the histogram
```
unique_words_hist(artist_obj_list, all_feat_artist=False, song_or_verse='verse', b=.01)
```
This vizualizes distributions by verse or by song of the (total unique words)/(all words) ratio. It can read in one or multiple artists
artist_obj_list: a list of artist objects
all_feat_artist = False: this will usually be set to false. Only set to true when bypassing the unique artist verse list described in rap clean (true means including featured artists vs)
song_or_verse = 'verse': user input if they want to vizualize by song or by verse
b = .01: bin size, .01 works well
```
unique_verses_bar(artist_obj_list, all_feat_artist=False, verse_count = 10)
```
This plots one or multiple artists verses ranked according to their (total unique words)/(all words) ratio and sized by their word count. It can find the top verses by this metric.
artist_obj_list: a list of artist objects
all_feat_artist = False: this will usually be set to false. Only set to true when bypassing the unique artist verse list described in rap clean (true means including featured artists vs)
verse_count = 10: how many verses to load into bar chart
```
unique_count_to_length(artist_obj_list, all_feat_artist=False, by_alb=False)
```
This plots a scatter plot where each point is a verse with the (total unique words)/(all words) ratio as the y axis and the average unique word length of the x axis. It can find verses with excptionally unique words or exceptionally long words and both
artist_obj_list: a list of artist objects
all_feat_artist = False: this will usually be set to false. Only set to true when bypassing the unique artist verse list described in rap clean (true means including featured artists vs)
by_alb = False: Purely used in coloration, when False, scatter points are colored by artist. When True, scatter points are colored by album
```
verse_search(artist_obj, song_name, verse_number=0)
```
This simple function can search an artist and pull out a verse from any song in that artists works.
artist_obj: an artist object - created in rap clean
song_name: the song name represented as a string
verse_number = 0: which verse to pull from the song
```
class line(self, word_objs)
```
This is a contianer object for word ojbects and their meta data
word_objs: a list of word objects that assemble into the line
ATTRIBUTES
line.word_objs: a 1d list of word objects making up the line
line.vowel_sounds: a 1d list representing the line as vowel sounds (used in creating graph colors)
line.all_cmu_vowel_sounds: a 1d list of all possible vowel sounds. Similar to line.vowel_sounds, but it contains all matching cmu possible vowel sounds for every word. This simple but powerful representation of possible vowel matching allows opto to run so quickly
line.word_to_vowels: a list of tuples. Each tuple is from a word object's matches attribute. This is used to colorize the graph
```
class verse_graph(self, verse_obj, artist_name, song_name)    
```
This is a way to graph verses according to color. It colorizes each syllable by broad, near, or exact matches.
verse_obj: a verse object created in rap_clean
artist_name: the artists name as a string
song_name: the song name as a string
ATTRIBUTES
verse_graph.ver_as_lines: this is a list of line objects, line objects described above
verse_graph.org_ver_as_lines: this is a deep copy of verse_graph.ver_as_lines. It's used when optimizing as the alogrithim starts from the original syllable breakdown.
```
verse_graph.verse_graph.opto_matches(self, pop=False, exc_line=False, opto_type='exact')
```
This is my favorite method ever. The algorithim isn't too complex. It essentially looks at all other lines within a radius of pop. It then will select a word's syllables (from the other possible syllable breakdonws in a rap_clean word object) and use whatever syllable has the most matches in that radius. It can optimize towards broad 'A', near 'AY', or exact 'AY0' syllable pariing (those syllables are how the CMU dict represents vowel sounds in words). It remakes verse_graph.ver_as_lines and writes a log of which syllables were changed
pop = False: False means it will use the whole verse in optimizing each word for matches. A number N means it will look N lines above and N lines below when optimizing (total of 2N lines)
exc_line = Flase: False means it will use the syllable breakdowns within the line the word lives in when optimizing matches. This is great for rappers that rhyme within the same line. True will exclude that line when scoring matches
opto_type = 'exact': this defines what vowel pairing it optimizes to. As explained earlier, it can look to make as many braod matches 'AY0'=='AI1', near matches 'AY0'=='AY1' or exact matches 'AY0'=='AY0' 
```
verse_graph.colorize_vowels(self, match_type='near')
```
This creates a color dictionary of vowel sounds to a color. It generates colors that are equally distant based on hex coloring. It uses match_type similarly to opto_type to color according to broad, near, or exact matches
verse_graph.match_type = 'near': broad, near, or exact matching as string
ATTRIBUTE
verse_graph.vowel_colors: a simple dictionary of vowel sounds to colors in this format (vowel sound:color)
```
verse_graph.graph_colored_verse(self)
```
This plots the colorized verse using html and css. It automatically creates the web based code and prints it out. It also stores the html file to pull up in another tab.
ATTRIBUTES
verse_graph.base_html: html (with css built in) breakdown of every word in a verse and colored accordingly 
Congrats on making it to the end! Didn't think anyone would TBH. Go color some verses!