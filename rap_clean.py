#import RAP_MASTER_LIB
from rap_db import *
import re
import psycopg2 as pg2
import psycopg2.extras
from nltk.corpus import stopwords
from nltk.stem import *
estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')

cur = estconn.cursor()
cur.execute('''SELECT lower(artist_nm) FROM all_artist_names UNION SELECT LOWER(artist_name) FROM artists;''')
query = cur.fetchall()
COMPLETE_RAPPERS = set()
#want all rappers listed and any rapper in list of rappers
for art in query:
    full_name = art[0]
    sep_name = re.sub('f./|f/|w/|&amp;|and|((^|\W)\()|(\)($|\W))', ',', full_name)
    list_of_names = sep_name.split(',')
    for name in list_of_names:
        COMPLETE_RAPPERS = COMPLETE_RAPPERS|{name.strip()}
COMPLETE_RAPPERS = COMPLETE_RAPPERS - {''}
cur.close()
estconn.close()

#quick way to check if it's a true verse
def check_verse(text, nec_len = 20, nec_uniq = 12):
    if len(text) < nec_len:
        return False
    unique_words = set()
    text_con = re.sub('[,\- \.\!]', '=.=', text)
    for word in text_con.split('=.='):
        unique_words = unique_words|{word.strip()}
    if len(unique_words) < nec_uniq:
        return False
    return True

class text_segment():
    def __init__(self, typ, label, start, end):
        self.typ = typ
        self.label = label
        self.start = start
        self.end = end
    def gen_content(self, raw_text, next_start):
        self.content = raw_text[self.end:next_start]

class verse(text_segment):
    def split_on_word(self):
        words = re.sub('[\n\.,\t!]', ' ', self.content)
        words = words.split(' ')
        self.all_words = list(filter(None, words))
        self.unique_words = set(self.all_words)
    
    def split_on_line(self):
        self.all_lines = list(filter(None, self.content.split('\n')))
        
    def split_on_stem(self):
        stemmer = SnowballStemmer("english")
        self.split_on_word()
        words_stm = [stemmer.stem(x) for x in self.all_words if stemmer.stem(x) not in stopwords.words('english')]
        self.all_stemmed_words = list(filter(None, words_stm))
        self.unique_stemmed_words = set(self.all_stemmed_words)
    
    def run_all_split(self):
        self.split_on_word()
        self.split_on_line()
        self.split_on_stem()

class song():
    #class variable -- regex are dope
    regex_commands = {'intro':'\[.*intro.*\]',
                      'outro':'\[.*outro.*\]',
                      'chorus':'(\[.*chorus.*\]|\(.*chorus.*\))',
                      'verse':'(\[.*verse.*|.*bridge.*\]|\(.*verse.*|.*bridge.*\))',                   
                      '[]':'\[(?!.*intro.*|.*outro.*|.*chorus.*|.*verse.*|.*bridge.*).*\]',
                      '{}':'\{(.*?)\}',
                      '\n':'\n',
                      '{**}':'\{\*(.*?)\*\}',
                      '()':'\((?!.*chorus.*|.*verse.*|.*bridge.*).*\)',
                      #made change here, more effect than thought
                      '""':'"[^"]*',
                      #'""':'"(.*?)"',
                      '?':'\?+',
                      '*text':'[\n| ]\*[^\n|\{|\(|\[]*'}
    
    def __init__(self, raw_text, name, artist):
        self.raw_text = re.sub('&amp;', 'and', raw_text)
        self.name = name
        self.artist = art
    
    #go through regex and compile dict and set of locaitons of each pattern match
    def assign_extras(self):
        self.extras = dict(zip(song.regex_commands.keys(), [[]]*len(song.regex_commands)))
        #set used later to create segments
        extra_segs = set()
        
        for ext, regex_command in song.regex_commands.items():
            finder = re.compile(regex_command)
            match_list = []
            for match in finder.finditer(self.raw_text.lower()):
                #match item has a start position and a label
                #seg_type here is used as an edge case when later adding in verses matched via artist name
                seg_type = ext
                #specialized check if an artist is saying lyric and immideitely add to verse list
                if match.group()[1:-1] in COMPLETE_RAPPERS:
                    seg_type = 'verse'
                    self.extras[seg_type].append((match.group(), (match.start(), match.start()+len(match.group()))))
                #if it doesn't mention an artist we just include it in the match list for now
                else:
                    match_list.append((match.group(), (match.start(), match.start()+len(match.group()))))
                
                #set mentioned earlier determines what segments will be used to construct actual song
                if seg_type in ['verse', 'chorus', 'intro', 'outro']:
                    extra_segs = extra_segs|{((seg_type, match.group()),(match.start(), match.start()+len(match.group())))}
            
            #now we all the mathces to the list of matching regex labels (verse, chorus, intro, etc.)
            self.extras[ext] = match_list
            
        #switchs to a list, this will be used for segment creation
        self.extra_segs = sorted(list(extra_segs), key=lambda x: x[1][0])
        
    #this removes any of the regex formations utilized above and recalculates all the new positions
    def remove_and_reass(self, rem = []):
        for r in rem:
            if r in song.regex_commands.keys():
                self.raw_text = re.sub(song.regex_commands[r], '', self.raw_text)
        self.assign_extras()
    
    #using our ordered list of regex matches from before, create a song out of the segments it's comprised of
    def create_song_as_seg(self):
        self.segments = []
        for index, extra in enumerate(self.extra_segs):
            ex_type = extra[0][0]
            ex_cont = extra[0][1]
            ex_start = extra[1][0]
            ex_end = extra[1][1]
            
            #first segment
            if not self.segments:
                seg = text_segment('[pre_text]', 'pre_text', 0, 0)
                #can simply reference next segment here
                seg.gen_content(self.raw_text, ex_start)
                self.segments = [seg]
            
            #create the actual segment to be appended to song
            seg = text_segment(ex_type, ex_cont, ex_start, ex_end)
            
            #to prevent error on the last segment, use alternate end position
            if index+1 == len(self.extra_segs):
                seg.gen_content(self.raw_text, len(self.raw_text))
            else:
                seg.gen_content(self.raw_text, self.extra_segs[index+1][1][0])
                
            #not all verse objects are truly verses, hence double check
            if seg.typ == 'verse':
                if check_verse(seg.content):
                    #if it passes, create verse object with special cleaning, properties, etc.
                    verse_seg = verse(seg.typ, seg.label, seg.start, seg.end)
                    verse_seg.content = seg.content
                    seg = verse_seg
                #if it was originally classified as a verse, but doesn't pass test, it's more of a chorus
                else:
                    seg.typ = 'chorus'
            self.segments.append(seg)

def flatten_to_segs(song_list):
    ret_list = []
    for cur_song in song_list:
        for seg in cur_song.segments:
            ret_list.append(seg)
    return ret_list

#album is a wrapper for holding songs, and verses, don't need it to hold song_segments but it can
class album():
    def __init__(self, artist, name, songs):
        self.name = name
        self.artist = artist
        self.songs = songs
        song_segments = flatten_to_segs(songs)
        self.verses = list(filter(lambda s: isinstance(s, verse), song_segments))
#aritst is similar but holds albums, songs and verses
class artist():
    def __init__(self, name, albums):
        self.name = name
        self.albums = albums
        self.songs = []
        self.verses = []
        for alb in albums:
            self.songs = self.songs + alb.songs
            self.verses = self.verses + alb.verses
            
#finally a function to build all this stuff
def construct_albums(albs_dic, artist_nm):
    albums = []
    for alb_name, sngs in albs_dic.items():
        song_objs = []
        for sng_name, lyrc in sngs.items():
            song_obj = song(lyrc, sng_name, artist_nm)
            song_obj.assign_extras()
            #MAJOR CHANGE HERE REVERT BACK IF YOU WANT THESE
            song_obj.remove_and_reass(['?', '*text', '()','{}','{**}'])
            song_obj.create_song_as_seg()
            song_objs.append(song_obj)
        album_obj = album(artist_nm, alb_name, song_objs)
        #extra verse cleaning
        for v in album_obj.verses:
            v.run_all_split()
        albums.append(album_obj)
    return albums

def construct_artists(conn, art_list = [''], alb_list = [''], sng_list = [''], use_ind_artists=False):
    record_pull = adv_pull(conn, art_list, alb_list, sng_list, use_ind_artists)
    artist_works = []
    for main_artist, db_records in record_pull.items():
        if use_ind_artists:
            for ind_art, ind_albs in db_records.items():
                artist_works.append(artist(ind_art, construct_albums(ind_albs, ind_art)))
        else:
            #key error means it didn't find anything for that artist
            artist_works.append(artist(main_artist, construct_albums(db_records[main_artist], main_artist)))
    return artist_works