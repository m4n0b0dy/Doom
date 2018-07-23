# Project Doom

Project Doom is a group of 4 Python libraries used for in depth analysis of rap lyrics. Doom specifically focuses on rap verses; where other libraries analyze every word within the lyrics of a song, Doom utilizes complex but robust filtering to extract verses and verses specific to individual artists.

Doom is written to be powerful enough for advanced programmers to use/tweak for their own research and simple enough for new comers/non-technical rap enthusiasts to utilize. By using container functions and detailing the start to finish, full scrape to visualization process in full_proc.ipynb, I hope people from all expertise backgrounds can enjoy and learn something new. Please use/tweak full_proc.ipynb for a simple and high level guide to using the libraries, this readme goes into depth regarding each function and object within each library.

Doom is broken up into 4 libraries, each designed with a focused purpose addressing the full scrape to visualization journey. Here are the libraries and their primary functionalities/capabilities (click one to read the documentation):

#### [rap_scrpr](#rap_scrpr-guide)

This library scrapes from a [rap lyrics website](http://ohhla.com). For the most part, lyrics are organized in a similar format with consistent labeling making the cleaning process relatively simple.

#### [rap_db](#rap_db-guide)
This library is comprised of a group of functions to interact with a PostgreSQL database full of rap lyrics. This type of analysis doesn't necessarily require a database, but using mass storage alows artist specific search, a powerful way to pull the desired lyrics. It manages the entire data storage process, table creation, populating the database, and quereying it.

#### [rap_clean](#rap_clean-guide)
This is the most complex of the four libraries as it tackles the most challenging part of textual data retrieval/cleaning. Per its name, it cleans and prunes lyrics stored in raw text data and extracts songs segments (intro, verse, chorus, outro, misc.). This project is dedicated to verses so there are additional filtering and objects/methods (word syllable extraction) within the verse object.

#### [rap_viz](#rap_viz-guide)
This library uses specialized artist, song, and verse objects created in rap_clean to visualize linguistic metadata, verse syllable breakdowns, and verse sorting/rankings. The functions in rap_viz can also be used as a template for creating complex, more specific, or more dynamic visualizations based on user preference.

#### rap_mach
This library is undergoing development. You may be able to guess by its name what it might do.

## Installing and Library Dependencies

### Installing Doom
```
pip install git+git://github.com/m4n0b0dy/doom
NEWCOMERS — This does not install all the other libraries necessary to run Doom (only installs my libraries)
```

### Library Dependencies
I'm not shy about using other libraries, and given the broad goals of each library, they use a ton of external functions. Here are the dependencies broken up by library; once a package has been listed, it isn't re-listed when imported again in a different Doom library. For your own sanity, I would HIGHLY recommend using Anaconda and installing all the unincluded ones individually.

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

## Project Doom Library Function and Object Guides

### rap_scrpr guide
```
pull_links(page_link, app, sng_scr=False)
```
This sub function pulls a list of links to feed into scraper. It may run twice if art_list page is in certain format (auto detects based on the album site).

page_link: link to page pulling links from (string)\
app: specialized character appending for certain art_list pages (string)\
sng_scr = False: indicating if it's one of those special artists (boolean)\
RETURNS: list of song links (list)
```
song_links(page_link, slept=.1)
```
This sub function takes in art_list/album links and uses pull_links to find song links (more of a wrapper function)

page_link: art_list page link (string)\
slept = .1: rest scraper between scrape to not overload host server (float)\
RETURNS: list of song links from art_list input  (list)
```
song_scrape(links, slept=1)
```
This function scrapes a list of SONG LINKS (must be song links)

links: song links (list of strings)\
slept = 1: sleep between song scrapes (without rest subject to 403 errors) (float)\
RETURNS: list of raw song texts (list of strings)
```
raw_clean(song_texts)
```
This very simple cleaning function loads in raw text and identifies art_list, album, song from data included in ohhla. If it can't id it, labels text "raw"

song_texts: list of song texts (list of strings)\
RETURNS: dictionary of cleaned song texts in this format dict(art_list:dict(albums:dict(titles:lyrics)))
```
scrape_multi_artists(conn, artist_list)
```
This function uses pull_link_from_art to pull each link for each art_list from DB. Then it iterates over art_list links and scrapes/applies above functions to each art_list and saves them to individual JSON files

conn: postgresql connection object\
artist_list: list of art_list names that map to DB records (list)\
RETURNS: list of names of new JSON files (list of strings)

### rap_db guide
Pretty much all functions in this library interact with our database of lyrics. Some are for data management/saving. Given their jobs, they don't return anything unless stating otherwise
```
create_music_tables(conn, bypass = False)
```
This function erases and creates 4 tables (base_artist, artists, albums, songs) that will hold our data

conn: postgresql connector object\
bypass = False: used to bypass the warning signal -warning cause you'd be erasing everything!-(boolean)
```
add_base(conn, base_art_name)
```
This function adds a special table to record which JSON file contributed what. It's not used later but helpful to refer back to ohhla

conn: postgresql connector object\
base_art_name: JSON file name — '.json' (string)
```
add_songs(conn, base_art_name, art_name, art)
```
This function adds songs to the DB! It uses the dictionary format we saved the JSON files in via rap_scrpr (art_list:album:song:lyrics)

conn: postgresql connector object\
base_art_name: json file name — '.json' (string)\
art_name: art_list name (string)\
art: art_list dictionary saved into JSON file in format dict(art_list:dict(albums:dict(titles:lyrics)))
```
percise_pull(conn, art, alb=False, song=False)
```
This is a deprecated but faster way to pull a song. It can pull all of an artists works, certain albums, or certain songs. However, it can only do one art_list at a time

conn: postgresql connector object\
art: art_list name (string)\
alb: album name (string)\
song: song name (string)\
RETURNS: dictionary consisting of this format dict(art:dict(art:dict(titles:lyrics)))
```
update_art_dic(art_dic, query, base_artist, use_ind_artists)

```
This function assists the adv_pull function by continually updating a dictionary that consists of an artists work. It outputs the same dictionary that inputs to keep updating it as more and more song are pulled

art_dic: a dictionary containing the full query information for an individual art_list, always organized dict(art_list:dict(albums:dict(titles:lyrics)))\
query: the returns of the DB query (dict formatted by column name to value)\
base_artist: user inputted artist name (string)\
use_ind_artists: set False (usually use user input art_list name). If it is true, the art_dic will be organized by the names in the DB which uses the ohhla true art_list name which can contain features, typos, etc. (boolean)\
RETURNS: continually updating dictionary for singular art_list dict(artist:dict(albums:dict(titles:lyrics)))
```
adv_pull(conn, artist_list = [''], album_list = [''], song_list = [''], use_ind_artists=False)
```
This function is more advanced than percise_pull. It can handle multiple artists, multiple albums, or multiple songs. As a result it has much simpler inputs but is slower

conn: postgresql connector object\
artist_list: art_list names to pull/filter form database (list of strings)\
album_list: album names to pull/filter form database (list of strings)\
song_list: song names to pull/filter form database (list of strings)\
use_ind_artists: use case described above (boolean)\
RETURNS: song info based on artist_list in this format dict(artist_list:dict(albums:dict(titles:lyrics)))
```
pull_link_from_art(conn, artist_name)
```
This pulls the ohhla link from a special table using an art_list name. Not vital but makes it really easy to scrape

conn: postgresql connector object\
artist_name: artist name that matches db record -case doesn't matter- (string)\
RETURNS: the ohhla link to scrape (string)
```
def bulk_load(conn, new_eds = [])
```
This is a wrapper function that uses the above functions to load in new JSON files into DB easily (DOES NOT RECREATE/ERASE TABLES)

conn: postgresql connector object\
new_eds: JSON files that are either in folder or in new_eds list (list of strings)
```
art_save(arts)
```
This has nothing to do with databases but is for data management. Once an art_list object is created, you can save it as a pickle file to a folder with this function. Create art_list objects involves a lot of cleaning and labeling so it greatly speeds process. Also eliminates need for database for high level art_list analysis

arts: artist objects to save (list of artist objects)
```
art_load(nms = set())
```
This loads those pickle files for quick and easy access. With no arguments, it loads all art_list objects in folder

nms = set(): references to art_list object names to load in -just the name, don't need to include.pkl- (list of strings)

### rap_clean guide
This is by far the most complex of the libraries. I wrote this library and it's guide in this order -functions that support objects, objects (with methods), functions that load/create/populate objects-. Because data cleaning is such an important part of data science, there are a lot of choices I made (reflected in the function argument line) in construction of each verse object. This is based on what I saw as the most efficient and accurate way to filter out non-verses. However, some may want to revisit my cleaning methodology, make improvements and filter differently: every function and object is equippied for revision.
```
check_verse(text, nec_len = 20, nec_uniq = 12)
```
This checks if a long string of lyrics is really a verese. By default, it must be at least 20 char long and have 12 unique words

text: text lyrics (string)\
nec_len = 20: minimum character count (integer)\
nec_uniq = 12: min unique word (integer)\
RETURNS: confirms check (boolean)
```
find_uniq_art_vers(ar, all_ver_lst, ratio_check=.5)
```
Similarly, this checks if a long string is really by the target art_list (not a features' verse) and shouldn't be classified as a chorus. By default, any text lyrics with 50% similarity are considered to be choruses (as they are repeated)

ar: art_list name, used to check if actually by art_list (string)\
all_ver_lst: all the verses we will check. They are all loaded in at once as they need to be compared to each other (set)\
ratio_check = .5: this is the minimum similarity that will trigger a False for a verse. If they have more than 50% similarity they aren't verses (float)\
RETURNS: art_list unique verses -later used as attribute- (list of verse objects)
```
flatten(container)
```
This simply takes a list, tuple, set, container that contains other containers and flattens every element until it is all in one container

container: list of lists, tuple of tuples, list of lists, etc.\
RETURNS: flattened container (list of containers)
```
claword(self, text):
```
This object is used to hold and analyze individual words. It can segment a word into vowel sounds and syllable sounds even when misspelled. It has only two methods but many attributes. __init__ runs complex functionality, but the overall goal is to match the count of vowel sounds to syllables for any given word

text: word (string)
Here are its attributes
```
word.text #the true word (string)
word.found_text #the closest word in CMU dict -same as word.text if in dict-(string)
word.all_found_words #5 words that are closest to word.txt (list)
word.vowel_sounds #the primary guess at the correct number of/vowel sounds of a word (list)
word.sylbl_sounds #the primary guess at the correct number of/syllable sounds of a word (list)
word.same_vowel_sounds #all possible vowel breakdowns that have the same length as word.sylbl_sounds (list)
word.matches #list of tuples in this format (syllable,vowel sound)
```
```
word.my_split(self, text_to_split, vowel_config, ap='', ap_num=False)
```
This is my custom splitting algorithm when traditional vowel and syllable breakdowns don't match in length (for colorization)

text_to_split: text that will run through algorithm (string)\
vowel_config: a vowel configuration used to match multiple syllable breakdowns (list)\
ap, ap_num: only used by other functions, no need to edit (used in special pronunciation edge cases) (string), (integer)\
```
spec_split(self, cur_vowel_config, regex_end, ap_syls)
```
This is used for special vowel combinations that product 1 or 0 vowels sounds "tion", "eve". These are matched on regex with an associated vowel count

cur_vowel_config: vowel breakdown of the word -fed into my_split-(list)\
regex_end: the regex used to find the special character combo (regex string)\
ap_syls: the number of vowel sounds that match is responsible for (integer)
```
word.sylbl_match(self)
```
This is a simple method that combines vowel sounds with syllable sounds. If no match is found, set attribute to unknown.
```
class text_segment(self, typ, label, start, end)
```
This is a basic text segment object. It can store where the text segment is for removal or analyze

typ: the type of text segment (held within regex class attribute of song) (string)\
label: the contents within the bracket, parentheses, curly bracets, etc. type (string)\
start: the position in the text where the label starts (integer)\
end: the position in the text where the content ends (integer)
``` 
text_segment.gen_content(self, raw_text, next_start)
```
This method extracts content from the text segment based on where the next text segment starts and contents of the current text segment

raw_text: the entire song (string)\
next_start: where the next text segment begins (integer)\
self.content = the content of that segment (string)
```
class verse(text_segment):
```
Uses inheritance from text segment. Everything is stored the same, when class song creates verse dictionaries, it utilizes the two checks described above
```
verse.split_to_words(self)
```
This splits the text segment into lines, and those lines into words. It then turns each word as a string into a word object (and runs word object methods). It stores these word objects in a dictionary (for speed and memory management) and other attributes for later use

verse.all_words_by_line: list of words, line by line (list of list of strings)\
verse.all_words: all words in verse (list of strings)\
verse.unique_words: all unique words in verse (set of lower case strings)\
self.word_objs: a dictionary in this format dict(word==typ(string):word==typ(word object))
```
class song(self, raw_text, name, art_list):
```
This takes in raw lyrics as text and creates segments out of them. Segments are text segments (with different types) or verses. Each verse goes through deeper analysis.

Attributes\
CLASS.regex_commands: text segment types and regex commands that can extract them. It is a class attribute as it will always be used dict(label:regex string)\
song.raw_text: lyrics (string)\
song.name: name of song (string)\
song.art_list: name of art_list (string)
```
song.assign_extras(self)
```
This goes through regex dictionary and finds every segment it can. It marks where it starts, where it ends and its content. It also does a quick check override for verses and saves special seg types that will eventually be created as text_segments

self.extras: every single text segment type and their matching start, end, content. Can be used for removal, text_segment creation, etc. dict(label:list of tuples of (integer, integer, string))\
self.extra_segs: a list of extras values that will be used to create the song as a segment, includes ['verse', 'chorus', 'intro', 'outro', '[]']
```
song.remove_and_reass(self, rems = [])
```
This goes through a list of types that we want to have removed from the song, removes them and their content and recalculates the extras

rems: types (regex dictionary keys) we want removed (list of strings)
```
song.create_song_as_seg(self)
```
This goes through self.extra_segs and creates each one into a text segment. It also creates/checks text segments if they should be verses and makes a verse object instead. It populates song.segments

Attributes\
song.segments: segment objects that make up a song (list of text_segment and verse objects)\
song.verses: just the verses (list of verse objets)\
song.uniq_art_verses: a list of verses that also passed the unique test listed earlier (list of verse objects)
```
flatten_songs(song_list)
```
This flattens a list of songs into one list to simplify making album and art_list container

song_list: list of song objects\
RETURNS: list of song objects
```
class album(self, art_list, name, songs)
```
This is a container object that holds song objects.

album.art_list: art_list name (string)\
album.name: album name (string)\
album.songs: all album songs (list of song objects)\
album.verses: all album verses (list of verse objects)\
album.uniq_art_verses: all album verses that also passed unique test (list of verse objects)
```
class art_list(self, name, albums)
```
This is another container at the art_list level. It has similar attributes to album but also contains albums. This overlap of information allows for more specific searching. Since objects are already created, it doesn't vastly increase time by copying them again (does increase total memory space)

art_list.name: art_list name (string)\
art_list.albums: artist's albums (list of album objects)\
album.songs: all artist songs (list of song objects)\
album.verses: all artist verses (list of verse objects)\
album.uniq_art_verses: all artist verses that also passed unique test (list of verse objects)
```
construct_albums(albs_dic, artist_nm)
```
Thifunction builds out art_list, album, song, text_segments, verses, word objects from a database pull. It takes in the artists name, and a dictionary in the format (album:song:lyrics) and makes appropriate objects

albs_dic: albums to songs to lyrics dict(albums:dict(titles:lyrics))\
artist_nm: the art_list we are creating's name (string)
```
construct_artists(conn, art_list = [''], alb_list = [''], sng_list = [''], use_ind_artists=False)
```
This function uses adv_pull from rap_db to pull an artists work from the database. It can search for multiple artists filtered by albums or songs

conn: a postgresql connection object\
artist_list: art_list names to pull/filter form database (list of strings)\
album_list: album names to pull/filter form database (list of strings)\
song_list: song names to pull/filter form database (list of strings)\
use_ind_artist: should be set as False. Only set to true when using the art_list names in the database over the art_list name used in select statement (boolean)\
RETURNS: newly made artist objects dict(art_list name as string:dict(art_list object with attributes listed above))

### rap_viz guide
All graphical visualizations are based on the amazing and easy to use Plotly library; since they are similar, their functional arguments are also similar. The syllable colorization visualization was written by me. They don't return anything as they plot the visualization in the notebook. I plan on recreating these functions with the ability to order/size according to multiple different metrics for later visualization/exploration
```
gen_plot(typ, traces, arts, b)
```
This supports the unique_words_hist which visualizes distributions by verse or by song of the (total unique words)/(all words) ratio

typ: 'verse' or 'song' (string)\
traces: these are plotly items that hold information about each datum point/bar\
arts: the artists used in the visualization (list of strings)\
b: the bin size of the histogram (float)
```
unique_words_hist(artist_obj_list, all_feat_artist=False, song_or_verse='verse', b=.01)
```
This visualizes distributions by verse or by song of the (total unique words)/(all words) ratio. It can read in one or multiple artists

artist_obj_list: artists to visualize (list of artist objects)\
all_feat_artist = False: this will usually be set too false. Only set to true when bypassing the unique art_list verse list described in rap clean -true means including featured artists vs-(boolean)\
song_or_verse = 'verse': user input if they want to visualize by song or by verse (string)\
b = .01: bin size, .01 works well (float)
```
unique_verses_bar(artist_obj_list, all_feat_artist=False, verse_count = 10)
```
Thiplots one or multiple artists verses ranked according to their (total unique words)/(all words) ratio and sized by their word count. It can find the top verses by this metric

artist_obj_list: artists to visualize (list of artist objects)\
all_feat_artist = False: this will usually be set too false. Only set to true when bypassing the unique art_list verse list described in rap clean -true means including featured artists vs-(boolean)\
verse_count = 10: how many verses to load into bar chart (integer)
```
unique_count_to_length(artist_obj_list, all_feat_artist=False, by_alb=False)
```
Thiplots a scatter plot where each point is a verse with the (total unique words)/(all words) ratio as the y-axis and the average unique word length of the x-axis. It can find verses with exceptionally unique words or exceptionally long words and both

artist_obj_list: artists to visualize (list of artist objects)\
all_feat_artist = False: this will usually be set too false. Only set to true when bypassing the unique art_list verse list described in rap clean -true means including featured artists vs-(boolean)\
by_alb = False: Purely used in coloration, when False, scatter points are colored by art_list. When True, scatter points are colored by album (boolean)
```
verse_search(artist_obj, song_name, verse_number=0)
```
This simple function can search an art_list and pull out a verse from any song in that artists works

artist_obj: artist (artist object)\
song_name: the song name (string)\
verse_number = 0: which verse to pull from the song (integer)
```
class line(self, word_objs)
```
Thiis a container object for word objects and their metadata

word_objs: words that assemble into the line (list of word objects)\
ATTRIBUTES\
line.word_objs: words making up the line (list of word objects)\
line.vowel_sounds: current vowel sounds of a line -used in creating graph colors-(list of strings)\
line.all_cmu_vowel_sounds: all possible vowel sounds. similar to line.vowel_sounds, but it contains all matching CMU possible vowel sounds for every word. this simple but powerful representation of possible vowel matching allows opto to run so quickly (list of strings)\
line.word_to_vowels: the word object's matches attribute. This is used to colorize the graph (list of tuples of (string, string))
```
class verse_graph(self, verse_obj, artist_name, song_name) 
```
This is a way to graph verses according to color. It colorizes each syllable by broad, near, or exact matches

verse_obj: the verse to analyze (verse object)\
artist_name: the artists (string)\
song_name: the song name (string)\
ATTRIBUTES\
verse_graph.ver_as_lines: linse to analyze (list of line objects)\
verse_graph.org_ver_as_lines: this is a deep copy of verse_graph.ver_as_lines. It's used when optimizing as the algorithm starts from the original syllable breakdown (list of line objects)
```
verse_graph.verse_graph.opto_matches(self, pop=False, exc_line=False, opto_type='exact')
```
This is my favorite method ever. The algorithm isn't too complex. It essentially looks at all other lines within a radius of pop. It then will select a word's syllables (from the other possible syllable breakdowns in a rap_clean word object) and use whatever syllable has the most matches in that radius. It can optimize towards broad 'A', near 'AY', or exact 'AY0' syllable pariing (those syllables are how the CMU dict represents vowel sounds in words). It remakes verse_graph.ver_as_lines and writes a log of which syllables were changed

pop = False: False means it will use the whole verse in optimizing each word (integer)
word for matches. A number N means it will look N lines above and N lines below when optimizing -total of 2N lines- (integer)\
exc_line = Flase: False means it will use the syllable breakdowns within the line the word lives in when optimizing matches. this is great for rappers that rhyme within the same line. True will exclude that line when scoring matches (boolean)\
opto_type = 'exact': this defines what vowel pairing it optimizes to. As explained earlier, it can look to make as many broad matches 'AY0'=='AI1', near matches 'AY0'=='AY1' or exact matches 'AY0'=='AY0' (string)
```
verse_graph.colorize_vowels(self, match_type='near')
```
This creates a color dictionary of vowel sounds to a color. It generates colors that are equally distant based on hex coloring. It uses match_type similarly to opto_type to color according to broad, near, or exact matches

verse_graph.match_type = 'near': broad, near, or exact matching (string)\
ATTRIBUTE\
verse_graph.vowel_colors: vowel sounds to colors in this format dict(vowel sound:color)
```
verse_graph.graph_colored_verse(self)
```
This plots the colorized verse using html and css. It automatically creates the web based code and prints it out. It also stores the html file to pull up in another tab

ATTRIBUTES\
verse_graph.base_html: html (with css built in) breakdown of every word in a verse and colored accordingly (string)\

Congrats on making it to the end! Didn't think anyone would TBH. Go color some verses!