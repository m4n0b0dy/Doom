import json
import re
from bs4 import BeautifulSoup
import urllib
import time
from rap_db import pull_link_from_art
#I don't like using try excepts but for scraping you don't want the whole thing to fail on an anamoloy
def pull_links(page_link, app, sng_scr=False):
	ret_list = []
	try:
		loaded = urllib.request.urlopen(page_link).read()
		soup = BeautifulSoup(loaded, 'html.parser')
		for a in soup.find_all('a'):
			if '.txt">' in str(a) or sng_scr:
			    lines = str(a).split('">')
			    match = re.search(r'href=[\'"]?([^\'" >]+)', lines[0])
			    link = match.group(1)
			    title = lines[1][:-4]
			    ret_list.append(app + link)
	except:
		#dont need notification of this
		if "//anonymous" not in page_link:
			print("Couldn't load", page_link)
	return ret_list

#find links to an artist's song
def song_links(page_link, slept=.1):
	#it's written like this because you can access lyrics straight from artist page for some
	#and others you must load each album - you can see which when opening page
	song_list = []
	if '.html' not in page_link:
		#third argument tells it to not just pull text files aka songs
		links = pull_links(page_link, page_link, True)
		for link in links:
			time.sleep(slept)
			song_list += pull_links(link, link)
	else:
		song_list = pull_links(page_link, 'http://ohhla.com/')
	song_list = [x for x in set(song_list) if "=" not in x and "//anonymous" not in x]
	return list(song_list)

#scrape the links
def song_scrape(links, slept=1):
	song_text = []
	for song in links:
		#was getting 403 errors from bad pages and effecting good pages
		#do this just in case so don't lose the whole scrape
		try:
			#load and parse lytics page
			page = urllib.request.urlopen(song).read()
			text = BeautifulSoup(page, 'html.parser')
			#can hit error cause sometimes pre isn't used
			try:
				lyrics_page = str(text.find_all('pre')[0])
			except:
				lyrics_page = str(text)
			#add text without all of the links	
			song_text.append(re.sub('<[^>]*>', '', lyrics_page))
		except:
			print("Couldn't scrape: "+song)
		#sleep to not overrun server
		time.sleep(slept)
	return song_text


#scraping is now all done, have to do intial clean
def raw_clean(song_texts):
	song_data = {}
	count_raw = 0
	count_clean = 0
	for song in song_texts:
		try:
			#sometimes artist is written incorrectly
			try:
				artist = re.search(r"Artist: (.*?)\n", song).group(1)
			except:
				artist = re.search(r"Aritst: (.*?)\n", song).group(1)
			#go through the strings identifying artist album etc.
			album = re.search(r"Album:  (.*?)\n", song).group(1)
			title = re.search(r"Song:   (.*?)\n", song).group(1)

			#sometimes doesn't pull typed right dur
			typed = re.search(r"Typed by: (.*?)\n", song).group(0)
			lyrics = song.split(typed,1)[1] 

			if artist not in song_data:
				song_data[artist] = {}
			if album not in song_data[artist]:
				song_data[artist][album] = {}
			song_data[artist][album][title] = lyrics

			count_clean += 1
		except:
			#again, want to use try excepts for indivdual artist
			song_data['raw_song_'+str(count_raw)] = song
			count_raw += 1
	print(str(count_raw)+" songs cleaned raw (not properly formatted)")
	print(str(count_clean)+" songs cleaned clean")
	return song_data

#scrape artist from list
def scrape_multi_artists(conn, artist_list):
    ret_list = []
    for art in artist_list:
        page = pull_link_from_art(conn, art)
        scraped_songs = raw_clean(song_scrape(song_links(page)))
        art_file = art.replace(' ', '_').lower()
        #back up scrape to json after clean
        with open('json_lyrics/'+art_file+'_raw.json', 'w') as outfile:
            json.dump(scraped_songs, outfile)
        print(art_file+'_raw.json made!')
        ret_list.append(art_file+'_raw.json')
    return ret_list