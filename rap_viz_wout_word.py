#crazies library
from statistics import mean, median
import re
import plotly.offline as offline
import plotly.figure_factory as ff
import plotly.graph_objs as go
from collections import Counter
from random import shuffle
from IPython.core.display import display, HTML
from rap_clean_w_word import *
RND = 3

def gen_plot(typ, traces, arts, b):
    fig = ff.create_distplot(traces, arts, bin_size=b, rug_text=traces, show_curve=True)
    layout = go.Layout(title='Unique Word Ratios by '+typ, hovermode=False)
    fig['layout'].update(layout)
    offline.iplot(fig)
    
def unique_words_hist(artist_obj_list, all_feat_artist=False, song_or_verse='verse', b=.01):
    verse_traces = []
    song_traces = []
    art_order = []
    offline.init_notebook_mode(connected=True)
    for art in artist_obj_list:
        art_order.append(art.name)
        #by verse
        uniq_vs = []
        #by song
        uniq_ss = []
        for sng in art.songs:
            one_song_uniqs = set()
            one_song_all = []
            if all_feat_artist:
                ver_iter = sng.verses
            else:
                ver_iter = sng.uniq_art_verses

            for v in ver_iter:
                #add this individual verse ratio
                uniq_vs.append(len(v.unique_words)/len(v.all_words))
                #add unique words in verses by artist
                one_song_uniqs = one_song_uniqs|v.unique_words
                #add words like a per capita
                one_song_all.extend(v.all_words)
            if one_song_uniqs and one_song_all:
                #then add the ratio to verses by song by artist
                uniq_ss.append(len(one_song_uniqs)/len(one_song_all))
                
        verse_traces.append(uniq_vs)
        song_traces.append(uniq_ss)
    if song_or_verse.lower() == 'verse':
        gen_plot('Verse', verse_traces, art_order, b)
    elif song_or_verse.lower() == 'song':
        gen_plot('Song', song_traces, art_order, b)
    else:
        gen_plot('Verse', verse_traces, art_order, b)
        gen_plot('Song', song_traces, art_order, b)

#my favorite funciton of all time tbh
def unique_verses_bar(artist_obj_list, all_feat_artist=False, verse_count = 10):
	#go through all artists, make a trace, plot them all
	#also works for ind artist
	traces = []
	ret_dic = {}
	offline.init_notebook_mode(connected=True)
	for art in artist_obj_list:
		#only iterating over songs so we can have song name too
		all_verses = []
		for sng in art.songs:
			ver_iter = []
			if all_feat_artist:
				ver_iter = sng.verses
			else:
				ver_iter = sng.uniq_art_verses
			for v_dex, v in enumerate(ver_iter):
				all_verses.append((len(v.unique_words)/len(v.all_words), v.content, len(v.all_words),sng.name, v_dex))  
		#outside of for loop to get all artist work not all song
		all_verses = sorted(all_verses, reverse=True)[:verse_count]
		#this dic is for info purposes
		ret_dic[art.name] = all_verses
		xs = []
		content = []
		#sort this again the other way I guess for desc looks
		for dex, a_v in enumerate(sorted(all_verses)):
			con = re.sub('\n+', '<br>',a_v[1]).rstrip('<br>').lstrip('<br>')
			xs.append(a_v[2])
			content.append(con+'<br>Song: "'+a_v[3]+'" - Verse: #'+str(a_v[4])+' - Score:('+str(round(a_v[0], RND))+')')

		trace = go.Bar(x=xs,
				orientation = 'h',
				text=content,
				#doesn't do anything right now
				textposition='bottom',
				width=.9,
				hoverinfo='text',
				name=art.name)
		traces.append(trace)
	#on to next artist if there is one
	layout = go.Layout(title='Top Unique Verses',
						barmode='stack',
						hovermode='closest',
						#want solution to text alignment left
						#https://stackoverflow.com/questions/50003531/r-plotly-hover-label-text-alignment
						xaxis=dict(title='Words in Verse',
						autorange=True,
						zeroline=False,
						showline=False),
						yaxis=dict(title='(Unique/All) Words per Verse',
						autorange=True,
						zeroline=False,
						showline=False,
						showticklabels=False))
	fig = go.Figure(data=traces, layout=layout)
	offline.iplot({'data': traces, 'layout': layout})
	return ret_dic

#nice! By album as well
def unique_count_to_length(artist_obj_list, all_feat_artist=False, by_alb=False):
	traces = []
	offline.init_notebook_mode(connected=True)
	for art in artist_obj_list:
		xs = []
		ys = []
		song_names = []
		for alb in art.albums:
			for sng in alb.songs:
				one_song_uniqs = set()
				one_song_all = []

				if all_feat_artist:
					ver_iter = sng.verses
				else:
					ver_iter = sng.uniq_art_verses

				for v in ver_iter:
					one_song_uniqs = one_song_uniqs|v.unique_words
					one_song_all.extend(v.all_words)
				if one_song_uniqs and one_song_all:
					xs.append(sum(map(len, one_song_uniqs))/float(len(one_song_uniqs)))
					ys.append(float(len(one_song_uniqs)/len(one_song_all)))
					song_names.append(sng.name)
			#if we are recording one color per album
			if by_alb:
				traces.append(go.Scatter(
						x = xs,
						y = ys,
						text=song_names,
						name=art.name+': '+alb.name,
						mode = 'markers',
						hoverinfo='text'))
				#reset song info as well
				xs = []
				ys = []
				song_names = []
		#if we are recording one color per artist
		if not by_alb:
			traces.append(go.Scatter(
						x = xs,
						y = ys,
						text=song_names,
						name=art.name,
						mode = 'markers',
						hoverinfo='text'))

	layout = go.Layout(title='Avg Unique Word Length by Count by Song',
	xaxis=dict(title='Avg Unique Word Length'),
	yaxis=dict(title='Unique Word Count'),
	hovermode='closest')
	fig = go.Figure(data=traces, layout=layout)
	offline.iplot({'data': traces, 'layout': layout})

#keep these as it just returns a verse
def verse_search(artist_obj, song_name, verse_number=0):
    for song_obj in artist_obj.songs:
        if song_name==song_obj.name and song_obj.uniq_art_verses:
            print('Found: '+song_name+'!')
            return song_obj.uniq_art_verses[verse_number]
    print("Couldn't Find: "+song_name)
    return None

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

#used in both vizualizing verses and optoing sylbl matching
class verse_graph():
    #these are used in opto and colorizing
    match_dic = {'broad':(0,1),'near':(0,-1),'exact':(None,None)}
    
    def __init__(self, verse_obj, artist_name, song_name):
        self.artist_name = artist_name
        self.song_name = song_name
        #double list comprehension biiih  -- this prdouced one list, I want list of lists
        #self.ver_as_lines = [verse_obj.word_objs[wrd] for cur_line in verse_obj.all_words_by_line for wrd in cur_line]
        self.ver_as_lines = [line([verse_obj.word_objs[wrd] for wrd in cur_line]) for cur_line in verse_obj.all_words_by_line]
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
            new_line_obj = line(line_obj.word_objs)
            optimized_lines.append(new_line_obj)
            
        #finally reset our verse lines to updated lines
        self.ver_as_lines = optimized_lines
        #and log changes
        print('Changed %i sylbs!'%change_count)
        if change_count > 0:
            with open('optos/opto_log_%s.txt'%self.song_name.lower().replace(' ','_'), 'w') as f:
                 f.write(opto_log)
    
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
    
    #use html to plot verse and save html version
    def graph_colored_verse(self):
        strt,end = verse_graph.match_dic[self.match_type]
        #make css
        self.base_html='''<html><style>h1{font-size:40pt;}h2{font-size:20pt;}
        mark{margin-right:-7.4px;font-family:Arial;font-size:14pt;background-clip:content-box;}
        mark:hover {cursor:help;position: relative}
        mark span {display:none}
        mark:hover span {display:block;z-index:1;white-space:nowrap;background:white;color:black;position:absolute;left:0px;margin:10px;top:10px;}'''
        legend = str()

        for vowel, v_color in self.vowel_colors.items():
            if vowel != 'unk':
                color_string = 'rgba('
                for rgb in v_color:
                    color_string+=str(rgb)+','
                color_string=color_string[:-1]+',.5)'
                self.base_html+='mark.'+vowel+'{background-color: '+color_string+';}'
            else:
                self.base_html+='mark.'+vowel[strt:end]+'{background-color: '+v_color+';}'
                vowel = vowel[strt:end]
                
            legend+='<mark class="'+vowel+'">'+vowel+'<span>(Count:%%'+vowel+'%%)</span></mark> '
        self.base_html+='</style><body><h1>Verse breakdown for '+self.song_name+' by '+self.artist_name+'</h1><h2>Vowel Color Legend<br></h2>'+legend+'<br><br>'
        #make legend
        every_vowel = []
        #make core html
        for line_obj in self.ver_as_lines:
            for word_to_vowel in line_obj.word_to_vowels:
                for sylb_w_vowel in word_to_vowel:
                    html_sylbl = sylb_w_vowel[1][strt:end]
                    every_vowel.append(html_sylbl)
                    self.base_html+='<mark class="'+html_sylbl+'">'+sylb_w_vowel[0]+'<span>(Sylbl:"'+sylb_w_vowel[0]+'", Vowel:'+html_sylbl+')</span></mark>'
                self.base_html+='     '
            self.base_html+='<br>'
        self.base_html=self.base_html.rstrip('<br>')
        self.base_html+='</body></html>'
        #update count in base html string
        for vwl, v_count in dict(Counter(every_vowel)).items():
            self.base_html=self.base_html.replace('%%'+vwl+'%%', str(v_count))
        #write to file
        with open('colorizations/%s_colorized.html'%self.song_name.lower().replace(' ','_'), 'w') as f:
            f.write(self.base_html.replace('margin-right:-7.4px;', 'margin-right:0px;'))