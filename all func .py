from statistics import mean, median
import re
import plotly.offline as offline
import plotly.figure_factory as ff
import plotly.graph_objs as go
from collections import Counter
from random import shuffle
from IPython.core.display import display, HTML
from rap_clean import *
from copy import deepcopy
RND = 3

def gen_plot(typ, traces, arts, b)
def unique_words_hist(artist_obj_list, all_feat_artist=False, song_or_verse='verse', b=.01)
#my favorite funciton of all time tbh
def unique_verses_bar(artist_obj_list, all_feat_artist=False, verse_count = 10)
#nice! By album as well
def unique_count_to_length(artist_obj_list, all_feat_artist=False, by_alb=False)
#searches an artists work and pulls a song and verse number
def verse_search(artist_obj, song_name, verse_number=0)
#mainly a container for words and meta word data
class line(self, word_objs)
#used in both vizualizing verses and optoing sylbl matching
class verse_graph(self, verse_obj, artist_name, song_name)    
    def opto_matches(self, pop=False, exc_line=False, opto_type='exact')
    #create a color dic corresponding to used vowel sounds
    def colorize_vowels(self, match_type='near')
    #use html to plot verse and save html version
    def graph_colored_verse(self)