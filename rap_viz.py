import matplotlib.pyplot as plt
from statistics import mean, median
from rap_clean import verse
import re
import plotly.offline as offline
import plotly.figure_factory as ff
import plotly.graph_objs as go
from nltk.corpus import cmudict
import pyphen
from collections import Counter
#from random import shuffle
from IPython.core.display import display, HTML

PYPHEN_DIC = pyphen.Pyphen(lang='en')
CMU_DICT = cmudict.dict()
CMU_KEYS = set(CMU_DICT.keys())
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
			for v in ver_iter:
				all_verses.append((len(v.unique_words)/len(v.all_words), v.content, len(v.all_words),sng.name))  
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
			content.append(con+'<br>Song: '+a_v[3]+' -- ('+str(round(a_v[0], RND))+')')

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