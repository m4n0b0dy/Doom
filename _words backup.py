
# coding: utf-8

# In[1]:

import RAP_MASTER_LIB
#MY LIBRARIES -- towards the end of project/when you need a break write up documentaiton of libraries
#another library for plotting and testing
from rap_scrpr import *
from rap_db import *
from rap_clean import*
from rap_viz import *

#estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
#import nltk
#nltk.download()
#create_music_tables(estconn)


# In[2]:

#new_artists = scrape_multi_artists(estconn, ['10sion'])
#create_music_tables(estconn, bypass = True)
#bulk_load(estconn, new_artists)
#lst = ['Del', 'Eminem', 'Jay-Z', 'Chance', '50_Cent', 'Doom']
#l2 = ['Sweatshirt']
#works_pull = dict(zip(lst, construct_artists(estconn, art_list = lst)))
#art_save(works_pull)


# In[3]:

lst = ['Del', 'Eminem', 'Jay-Z', 'Chance', '50_Cent', 'Doom', 'Earl']
works = art_load(lst)


# In[4]:

sub_works = {'Del':works['Del'], 'Chance':works['Chance'], 'Doom':works['Doom'], 'Earl':works['Earl']}


# In[5]:

vs = unique_verses_bar(sub_works.values())


# In[6]:

unique_words_hist(sub_works.values())


# In[7]:

unique_words_hist(sub_works.values(), song_or_verse='song')


# In[8]:

unique_count_to_length(sub_works.values())


# In[9]:

unique_count_to_length([works['Del']], by_alb=True)


# In[10]:

#functions used by classes
def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i
def verse_search(artist_obj, song_name, verse_number=0):
    for song_obj in artist_obj.songs:
        if song_name==song_obj.name and song_obj.uniq_art_verses:
            print('Found: '+song_name+'!')
            return song_obj.uniq_art_verses[verse_number]
    print("Couldn't Find: "+song_name)
    return None


# In[11]:

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


# In[12]:

class line():
    def __init__(self, raw_text):
        words = re.sub("[^0-9a-zA-Z\']+", ' ', raw_text)
        self.words = list(filter(None, words.split(' ')))
        self.word_objs = [word(wrd) for wrd in self.words]
        line.make_line_attr(self)
        
    def make_line_attr(self):
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


# In[48]:
class verse_graph():
    #these are used in opto and colorizing
    match_dic = {'broad':(0,1),'near':(0,-1),'exact':(None,None)}
    
    def __init__(self, verse_obj, artist_name, song_name):
        self.artist_name = artist_name
        self.song_name = song_name
        self.ver_as_lines = [line(line_obj) for line_obj in verse_obj.all_lines]
        self.org_ver_as_lines = self.ver_as_lines
            
    def opto_matches(self, pop=False, exc_line=False, opto_type='exact'):
        strt,end = verse_graph.match_dic[opto_type]
        self.ver_as_lines = self.org_ver_as_lines
        if not pop:
            pop=int(len(self.ver_as_lines)/2)
        optimized_lines = []
        opto_log=''
        change_count=0
        for dex, line_obj in enumerate(self.ver_as_lines):
            #this picks the lines within population before current line after current line
            nearby_lines = self.ver_as_lines[max(0,dex-pop):dex+pop+1]
            #deleting selected current line
            if exc_line:
                del nearby_lines[-pop-1]
            all_nearby_vowels = []
            for nearby_line in nearby_lines:
                #this creates a list of all vowel sounds (broad, near, or exact) within the nearby_lines population
                all_nearby_vowels.extend([all_v[strt:end] for all_v in nearby_line.all_cmu_vowel_sounds])
            count_nearby_vowels = dict(Counter(all_nearby_vowels))
            #will use that count_nearby_vowels to compare scores when picking new vowel soudn
            new_word_objs=[]
            for wrd_dex, wrd in enumerate(line_obj.word_objs):
                #only change if there are alternate vowel soundings and we know the current vowel sound
                if len(wrd.same_vowel_sounds)>1 and wrd.matches[0][1]!='unk':
                    final_config = wrd.matches
                    for sylbl_config in wrd.same_vowel_sounds:
                        #this complicated thing just combines all the current sylbs and possible sylbs and makes sure they're in the dic
                        #only important when excluding the current line from the count
                        sylbl_set_check = set([all_v[strt:end] for all_v in list(zip(*final_config))[1]])|set([all_v[strt:end] for all_v in sylbl_config])
                        if sylbl_set_check.issubset(set(count_nearby_vowels.keys())):
                            new_config=[]
                            for test, current, sylbl in zip(sylbl_config, list(zip(*final_config))[1], wrd.sylbl_sounds):
                                #go through each words alterante sylbs and reassign that sylbl if it occurs more within nearby lines 
                                if count_nearby_vowels[test[strt:end]] > count_nearby_vowels[current[strt:end]]:
                                    new_config.append((sylbl, test))
                                    #log it
                                    change_count+=1
                                    opto_log = opto_log+'Change #'+str(change_count)+'-loc(Line:'+str(dex)+', Word:'+str(wrd_dex)+'): Within "'+wrd.text+'" changed "'+sylbl+'" from "'+current+'('+str(count_nearby_vowels[current[strt:end]])+')" to "'+test+'('+str(count_nearby_vowels[test[strt:end]])+')"\n'
                                else:
                                    #otherwise use the same sylbl
                                    new_config.append((sylbl, current))
                            final_config = new_config
                    #change the vowel sound of core word -  for consistency
                    wrd.vowel_sounds = list(zip(*final_config))[1]
                    #change instance attribute to new final_config
                    wrd.matches = final_config
                #append new words for each line
                new_word_objs.append(wrd)
            #set the lines word objects equal to our new words
            line_obj.word_objs = new_word_objs
            #remake the line attributes with this new word list
            line_obj.make_line_attr()
            optimized_lines.append(line_obj)
            
        #finally reset our verse lines to updated lines
        self.ver_as_lines = optimized_lines
        #and log changes
        print('Changed '+str(change_count)+' sylbs!')
        text_file = open('opto_log_'+self.song_name+'.txt', 'w')
        text_file.write(opto_log)
        text_file.close()
    
    #create a color dic corresponding to used vowel sounds
    def colorize_vowels(self, match_type='near'):
        self.match_type = match_type
        all_vowels = set(flatten([line_obj.vowel_sounds for line_obj in self.ver_as_lines]))-{'unk'}
        strt,end = verse_graph.match_dic[self.match_type]
        vowels_used = set([all_v[strt:end] for all_v in all_vowels])

        max_value = 16581375 #255**3
        interval = int(max_value / len(vowels_used))
        colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]
        color_list = [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]
        shuffle(color_list)
        self.vowel_colors = dict(zip(vowels_used, color_list))
        self.vowel_colors.update({'unk':'transparent'})
    
    #use html to plot verse
    def graph_colored_verse(self):
        strt,end = verse_graph.match_dic[self.match_type]
        #make css
        self.base_html='<html><style>h1{font-size:40pt;}mark{margin-right: -7.4px;font-family:Arial;font-size:14pt;background-clip:content-box;}'
        for vowel, v_color in self.vowel_colors.items():
            if vowel != 'unk':
                color_string = 'rgba('
                for rgb in v_color:
                    color_string+=str(rgb)+','
                color_string=color_string[:-1]+',.5)'
                self.base_html+='mark.'+vowel+'{background-color: '+color_string+';}'
            else:
                self.base_html+='mark.'+vowel[strt:end]+'{background-color: '+v_color+';}'
                
        self.base_html+='</style><body><h1>Verse breakdown for '+self.artist_name+'</h1><br>'
        #make core html
        for line_obj in self.ver_as_lines:
            for word_to_vowel in line_obj.word_to_vowels:
                for sylb_w_vowel in word_to_vowel:
                    html_sylbl = sylb_w_vowel[1][strt:end]
                    self.base_html+='<mark class="'+html_sylbl+'">'+sylb_w_vowel[0]+'</mark>'
                self.base_html+='     '
            self.base_html+='<br>'
        self.base_html=self.base_html.rstrip('<br>')
        self.base_html+='</body></html>'


# In[49]:

artist_name = 'Doom'
song_name = 'Bada Bing'
bada_bing = verse_graph(verse_search(works[artist_name], song_name), artist_name, song_name)


# In[50]:

bada_bing.colorize_vowels('near')
bada_bing.graph_colored_verse()
display(HTML(bada_bing.base_html))


# In[51]:

bada_bing.opto_matches(pop=2, exc_line=False, opto_type='exact')
bada_bing.colorize_vowels('near')
bada_bing.graph_colored_verse()
display(HTML(bada_bing.base_html))


# In[ ]:




# In[17]:

#like to find a song that uses opto well
artist_name = 'Chance'
song_name = 'Favorite Song'
fav_song = verse_graph(verse_search(works[artist_name], song_name, verse_number=0), artist_name, song_name)

fav_song.colorize_vowels(match_type='exact')
fav_song.graph_colored_verse()
display(HTML(fav_song.base_html))


# In[18]:

#like to find a song that uses opto well
artist_name = 'Del'
song_name = 'Virus'
virus = verse_graph(verse_search(works[artist_name], song_name, verse_number=1), artist_name, song_name)

virus.colorize_vowels(match_type='near')
virus.graph_colored_verse()
display(HTML(virus.base_html))


# In[19]:

v_type = 'near'
virus.opto_matches(pop=2, exc_line=False, opto_type=v_type)
virus.colorize_vowels(match_type=v_type)
virus.graph_colored_verse()
display(HTML(virus.base_html))


# Just some of the exceptions
# need to re run to get all of them
# {'austria': (3, ['aus', 'tria']),
#  'creations': (3, ['cre', 'ations']),
#  'equestrian': (4, ['eques', 'tri', 'an']),
#  'equivalence': (4, ['equiv', 'a', 'lence']),
#  'fumbling': (3, ['fum', 'bling']),
#  'imm': (3, ['imm']),
#  "it'll": (2, ["it'll"]),
#  'opera': (2, ['opera']),
#  'ruffling': (3, ['ruf', 'fling']),
#  'simpler': (3, ['sim', 'pler']),
#  'societies': (4, ['so', 'ci', 'eties']),
#  'struggling': (3, ['strug', 'gling']),
#  'stumbling': (3, ['stum', 'bling']),
#  "that'll": (2, ["that'll"]),
#  'unique': (2, ['unique']),
#  'unsettling': (4, ['un', 'set', 'tling']),
#  'visualize': (3, ['vi', 'su', 'al', 'ize'])}

# what you did
# went line by line through code to add to rap viz
# remade word opbject to A) try all vowel combos for all vowel words against all sylbl options (this includes using PYPHEN first against all vowel configs to prevent the extra shit - sped and simplified)
# remade otpo to only look at sylb vowel configs that match in length
# added to rap viz!
# 
# what's next
# next viz!
# 
# down the line
# keep modeling and coming up with stuff!
# 
# for verse example use bada bing

# In[20]:

#estconn.close()


