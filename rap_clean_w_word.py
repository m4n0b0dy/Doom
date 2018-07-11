#import RAP_MASTER_LIB
from rap_db import *
import re
import psycopg2 as pg2
import psycopg2.extras
from nltk.corpus import stopwords
from nltk.stem import *
from difflib import SequenceMatcher
from difflib import get_close_matches
PYPHEN_DIC = pyphen.Pyphen(lang='en')
CMU_DICT = cmudict.dict()
CMU_KEYS = set(CMU_DICT.keys())

#only change run if DB has changed
run = True
if run:
     #try to load our complete rappers fresh from db, but if it's not there just take the most recent picle file
    try:
        estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
        cur = estconn.cursor()
        cur.execute('''SELECT LOWER(artist_nm) FROM all_artist_names UNION SELECT LOWER(artist_name) FROM artists;''')
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
        #repurposing my save and load functions
        art_save({'COMPLETE_RAPPERS':COMPLETE_RAPPERS})
    except:
        COMPLETE_RAPPERS = art_load(nms=['COMPLETE_RAPPERS'])['COMPLETE_RAPPERS']
else:
    COMPLETE_RAPPERS = art_load(nms=['COMPLETE_RAPPERS'])['COMPLETE_RAPPERS']


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

#this specialized function pulls out verses that are by specific artist (not features) and don't match any other verse to 50%
def find_uniq_art_vers(ar, all_ver_lst, ratio_check=.5):
	all_vers = set(all_ver_lst)
	ret_vers = set()
	for vers in all_vers:
		lb = vers.label.lower()
		#first check that verse is by artist or general
		art_ch = (ar.lower() in lb or re.match('[^a-z0-9\-](verse|bridge)[^a-z0-9\-]', lb))
		#then make sure verse is unique
		new_ch = True
		for prev_ver in all_vers - {vers}:
            #there is an "issue" that the repeated verses will never be added, however, repeated verses are usually really choruses so it kinda works
			if SequenceMatcher(None, prev_ver.content, vers.content).ratio() > ratio_check:
				new_ch = False
		if art_ch and new_ch:
			ret_vers = ret_vers|{vers}
	return list(ret_vers)

def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i

#used to hold and breakdown words
class word():
    #deconstruct word into vowel sounds and sylbl sounds and match them
    def __init__(self, text):
        self.text = re.sub("'",'', text)
        if self.text.isdigit():
            #this expression is used when returning unknown, needed for later
            self.found_text, self.same_vowel_sounds, self.matches = None, ['unk'], list(zip([self.text], ['unk']))
            return None
        
        #found text will always be the word or guess at what the word is
        self.found_text = self.text.lower()
        #all found words serves as all possible matches for known or unknown words
        self.all_found_words = set([self.found_text])
        
        if self.found_text not in CMU_KEYS:
            self.all_found_words = get_close_matches(self.found_text, CMU_KEYS, n=5)
            if not self.all_found_words:
                print('Error with '+self.text)
                self.found_text, self.same_vowel_sounds, self.matches = None, ['unk'], list(zip([self.text], ['unk']))
                return None
            self.found_text = self.all_found_words[0]
            #the best and nearest match contains similar number of chars as word, opto later helps with this
            for fnd_word in self.all_found_words:
                if len(fnd_word)>=len(self.text):
                    self.found_text = fnd_word
                    break
                    
        #first attempt at sylbl matching. Use self.text because there's no gain to splitting the wrong word
        self.sylbl_sounds = PYPHEN_DIC.inserted(self.text).split('-')
        #first attempt at vowel matching using first vowel config
        self.vowel_sounds = list(filter(re.compile(r'[aeiou]+', re.IGNORECASE).match, CMU_DICT[self.found_text][0]))
        #this will be used to assign a current vowel config if there's a better match
        #and store other words/vowel configs later to find the most appropriate during sylbl searching and optoing
        matched = False
        all_vowel_sounds = []
        for found_word in self.all_found_words:
            for mtch in CMU_DICT[found_word]:
                #expression pulls out vowel sounds from match
                mtch_vowel_sounds = list(filter(re.compile(r'[aeiou]+', re.IGNORECASE).match, mtch))
                #use list to maintain order (everything is ordered from CMU/get_close_matches)
                all_vowel_sounds.append(tuple(mtch_vowel_sounds))
                #if it matches sylbl_sounds use the first match as current vowel conf
                if len(mtch_vowel_sounds) == len(self.sylbl_sounds) and not matched:
                    self.vowel_sounds = mtch_vowel_sounds
                    matched = True
        
        #if they aren't equal aka no break try my own splitting algo - resets self.sylbl_sounds if it finds a better match
        dex = 0
        while len(self.vowel_sounds)!=len(self.sylbl_sounds) and dex!=len(all_vowel_sounds):
            #want to run this for all possible vowel combos as thoroughly possible
            #using self.text allows us to print the true text, with the found texts match
            word.my_split(self, self.text, all_vowel_sounds[dex])
            dex+=1
        
        #only use these in opto (only want matching vowel sounds)
        self.same_vowel_sounds = set([config for config in all_vowel_sounds if len(config)==len(self.sylbl_sounds)])
        word.sylbl_match(self)
      
    def my_split(self, text_to_split, vowel_config, ap='', ap_num=False):
        vowels = 4
        sylbl_sound_try = []
        #test by segmented words on {,4} sylbs, then {,3}, then {,2}, then {,1}, %%% is for my special cases which come later
        while len(vowel_config)!=len(sylbl_sound_try) and vowels>0:
            sylbl_sound_try = re.findall(r'(%%%|[^aeiouy%]*[aeiouy]{,'+str(vowels)+'}[^aeiouy%]*)', text_to_split, re.IGNORECASE)
            sylbl_sound_try = list(filter(None, sylbl_sound_try))
            vowels-=1
        #this is after running spec_split, ap = the special text, ap_num indicates how many  - this is for 0 sylbl
        if ap_num == 0 and ap != '':
            #find temp palceholder %%%
            found = sylbl_sound_try.index('%%%')
            #if it's the first sylbl add to start of second
            if found == 0:
                sylbl_sound_try[1] = ap+sylbl_sound_try[1]
            #otherwise add to previous sylbl
            else:
                sylbl_sound_try[found-1] = sylbl_sound_try[found-1]+ap
            sylbl_sound_try.remove('%%%')
        #for 1 sylbl spec cases, simply replace %%% with ap
        elif ap_num == 1 and ap != '':
            sylbl_sound_try = [ap if mtch=='%%%' else mtch for mtch in sylbl_sound_try]
            
        #check if we found the match (this runs before and after spec_split)
        if len(vowel_config)==len(sylbl_sound_try):
            self.sylbl_sounds = sylbl_sound_try
            return
        
        #triggers if we haven't run spec_split yet to prevent infinite recursive loop
        elif not ap_num and ap == '':
            #dictionary of special split types and their sylbl count - subject to change
            reg_exs = {#silent edge cases (de, te, le, ey, plurals, past tense) at the end of word
                        r'.*?(e[sd]|[^aeiouy][ey])$':0,
                        #1 sylbl edge cases anywhere in word
                        r'.*?([^aeiouy]*eve)*.*':1,
                        #1 sylbl edge cases at the end of a word
                        r'.*?(tion*)$':1}
            #feed them into spec_split
            for reg_ex, sylbl_count in reg_exs.items():
                word.spec_split(self, vowel_config, reg_ex, sylbl_count)
                #if succesful break out of for loop
                if len(vowel_config)==len(self.sylbl_sounds):
                    #must break here because earlier return (with assignment) just goes back to spec_split and keeps running this for loop
                    break

    #this is used for known special splitting for 0 or 1 sylbl sounds using unique vowel combos
    def spec_split(self, cur_vowel_config, regex_end, ap_syls):
        #using self.text allows us to print the true text, with the found texts match
        matched = re.match(regex_end, self.text, re.IGNORECASE)
        if matched:
            if matched.group(1):
                matched = matched.group(1)
                rep_matched = self.text.replace(matched,'%%%')
                word.my_split(self, rep_matched, cur_vowel_config, ap=matched, ap_num=ap_syls)
                
    #this function matches vowel sylbls to word sylbls for colorizing
    def sylbl_match(self):
        self.matches = list(zip(self.sylbl_sounds, ['unk']*len(self.sylbl_sounds)))
        if len(self.sylbl_sounds) == len(self.vowel_sounds):
            self.matches = list(zip(self.sylbl_sounds, self.vowel_sounds))

#mainly a container for words and meta word data
class line():
    def __init__(self, word_objs):
        self.word_objs = word_objs
        self.vowel_sounds = []
        self.all_cmu_vowel_sounds = []
        self.word_to_vowels = []
        for cur_wrd in self.word_objs:
            #used in color dictionary creation
            self.vowel_sounds.extend(list(zip(*cur_wrd.matches))[1])
            #this is for the viz
            self.word_to_vowels.append(cur_wrd.matches)            
            #this will be used in optimization
            self.all_cmu_vowel_sounds.extend(flatten(flatten(cur_wrd.same_vowel_sounds)))

class text_segment():
    def __init__(self, typ, label, start, end):
        self.typ = typ
        self.label = label
        self.start = start
        self.end = end
    def gen_content(self, raw_text, next_start):
        self.content = raw_text[self.end:next_start]

#run word dictionary to store temp word types
#fix lower so you don't need to store as lower
#^ adjust accordingly in rap viz
#build/store line types here as well
#MADE LOWER CHANGE, ADJUSTED IN RAP VIZ AS WELL
#needs testing
#can add easier analtrics attribuest later like sylbl distr, sentiment, etc.
class verse(text_segment):
    def split_on_word(self):
        words = re.sub("[^0-9a-zA-Z\'\n]+", ' ', self.content)
        words = words.split(' ')
        #no need for lower here
        self.all_words = list(filter(None, words))
        self.unique_words = set()
        self.dic_word_objs = {}
        #want unique words to capture word in purest form for making word object
        for wrd in set(self.all_words)-{'\n'}:
            #want to maintain text so no lower
            self.dic_word_objs[wrd] = word(wrd)
            #want true uniques so use lower
            self.unique_words = self.unique_words|set(wrd.lower())
    #this now holds what was in verse_graph
    def split_on_line(self):
        self.ver_as_lines = []
        cur_line = []
        for wrd in self.all_words:
            if wrd == '\n':
            	#holds line objects
            	self.ver_as_lines.append(line(cur_line))
                cur_line = []
            else:
                cur_line.append(self.dic_word_objs[wrd])
        self.all_words = [wrd for wrd in self.all_words if wrd != '\n']

    def split_on_stem(self):
        stemmer = SnowballStemmer("english")
        self.split_on_word()
        words_stm = [stemmer.stem(x.lower()) for x in self.all_words if stemmer.stem(x.lower()) not in stopwords.words('english')]
        self.all_stemmed_words = list(filter(None, words_stm))
        self.unique_stemmed_words = set(self.all_stemmed_words)
    
    def run_all_split(self):
        self.split_on_word()
        self.split_on_line()
        #self.split_on_stem()

class song():
    #class variable -- regex are dope
    regex_commands = {'intro':'\[.*intro.*\]',
                      'outro':'\[.*outro.*\]',
                      'chorus':'(\[.*chorus.*\]|\(.*chorus.*\))',
                      'verse':'(\[.*verse.*|.*bridge.*\]|\(.*verse.*|.*bridge.*\))',
                      '[]':'\[(?!.*chorus.*|.*verse.*|.*bridge.*|.*intro.*|.*outro.*).*\]',
                      '{}':'\{(.*?)\}',
                      '\n':'\n',
                      '{**}':'\{\*(.*?)\*\}',
                      '()':'\((?!.*chorus.*|.*verse.*|.*bridge.*).*\)',
                      '""':'"[^"]*',
                      '""':'\*[^\*]*',
                      '?':'\?+',
                      '*text':'[\n| ]\*[^\n|\{|\(|\[]*'}
    
    def __init__(self, raw_text, name, artist):
        self.raw_text = re.sub('&amp;', 'and', raw_text)
        self.name = name
        self.artist = artist
    
    #go through regex and compile dict and set of locaitons of each pattern match
    def assign_extras(self):
        self.extras = dict(zip(song.regex_commands.keys(), [[]]*len(song.regex_commands)))
        #set used later to create segments
        extra_segs = set()
        for ext, regex_command in song.regex_commands.items():
            #this should fix the lower issue
            finder = re.compile(regex_command, re.IGNORECASE)
            match_list = []
            for match in finder.finditer(self.raw_text):
                #match item has a start position and a label
                #seg_type here is used as an edge case when later adding in verses matched via artist name
                seg_type = ext
                #specialized check if an artist is saying lyric and immideitely add to verse list
                #if low_mtch[1:-1] in COMPLETE_RAPPERS or 'verse' in low_mtch or 'bridge' in low_mtchor 'intro' in low_mtch or 'outro' in low_mtch:
                if match.group().lower()[1:-1] in COMPLETE_RAPPERS:
                    seg_type = 'verse'
                    self.extras[seg_type].append((match.group(), (match.start(), match.start()+len(match.group()))))
                #if it doesn't mention an artist we just include it in the match list for now
                else:
                    match_list.append((match.group(), (match.start(), match.start()+len(match.group()))))
                
                #set mentioned earlier determines what segments will be used to construct actual song
                #ATTEMPT AT EXTRA NON VERSE WORDS INSIDE MY VERSE OBJECTS
                if seg_type in ['verse', 'chorus', 'intro', 'outro', '[]']:
                #original > if seg_type in ['verse', 'chorus', 'intro', 'outro']:
                    extra_segs = extra_segs|{((seg_type, match.group()),(match.start(), match.start()+len(match.group())))}
            
            #now we all the mathces to the list of matching regex labels (verse, chorus, intro, etc.)
            self.extras[ext] = match_list
            
        #switchs to a list, this will be used for segment creation
        self.extra_segs = sorted(list(extra_segs), key=lambda x: x[1][0])
        
    #this removes any of the regex formations utilized above and recalculates all the new positions
    def remove_and_reass(self, rems = []):
        for rem in rems:
            matches = self.extras[rem]
            for match in matches:
                self.raw_text = re.sub(re.escape(match[0]), '', self.raw_text)
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
                    verse_seg.run_all_split()
                    seg = verse_seg
                #if it was originally classified as a verse, but doesn't pass test, it's more of a chorus
                else:
                    seg.typ = 'chorus'
            self.segments.append(seg)
        self.verses = list(filter(lambda s: isinstance(s, verse), self.segments))
        self.uniq_art_verses = find_uniq_art_vers(self.artist, self.verses)
#simple function to pull song info
def flatten_songs(song_list):
    #ret_segs, ret_verses, ret_uniq_art_verses = [], [], []
    ret_verses, ret_uniq_art_verses = [], [], []
    for cur_song in song_list:
        #ret_segs = ret_segs + cur_song.segments
        ret_verses = ret_verses + cur_song.verses
        ret_uniq_art_verses = ret_uniq_art_verses + cur_song.uniq_art_verses
    #return ret_segs, ret_verses, ret_uniq_art_verses
    return ret_verses, ret_uniq_art_verses

#album is a wrapper for holding songs, and verses, don't need it to hold song_segments but it can
#as verse grows more complex and I segment less by album, etc, may want to get rid of this - not yet just a thought
#^per this thought, gonna only store vereses in artist not segments
class album():
    def __init__(self, artist, name, songs):
        self.name = name
        self.artist = artist
        self.songs = songs
        #only gonna store verses
        #self.segments, self.verses, self.uniq_art_verses = flatten_songs(self.songs)
        self.verses, self.uniq_art_verses = flatten_songs(self.songs)
#aritst is similar but holds albums, songs and verses
class artist():
    def __init__(self, name, albums):
        self.name = name
        self.albums = albums
        self.songs = []
        #self.segments = []
        self.verses = []
        self.uniq_art_verses = []
        for alb in albums:
            self.songs = self.songs + alb.songs
            #self.segments = self.segments + alb.segments
            self.verses = self.verses + alb.verses
            self.uniq_art_verses = self.uniq_art_verses + alb.uniq_art_verses

#finally a function to build all this stuff
def construct_albums(albs_dic, artist_nm):
    albums = []
    for alb_name, sngs in albs_dic.items():
        song_objs = []
        for sng_name, lyrc in sngs.items():
            song_obj = song(lyrc, sng_name, artist_nm)
            song_obj.assign_extras()
            song_obj.remove_and_reass(['[]', '?', '*text', '{**}']) 
            song_obj.create_song_as_seg()
            song_objs.append(song_obj)
        album_obj = album(artist_nm, alb_name, song_objs)
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