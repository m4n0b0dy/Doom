import json
import re
from bs4 import BeautifulSoup
import urllib
import time

#can make this fully automated with the a little more parsing!
#also fix the error that prints couldnt load

def pull_links(page_link, app = '', sng_scr=False):
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
		print("Couldn't load", page_link)
	return ret_list

#find links to an artist's song
def song_links(page_link, alt=False, slept=.1):
	#it's written like this because you can access lyrics straight from artist page for some
	#and others you must load each album - you can see which when opening page
	song_list = []
	if alt:
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
		#do this just in case so we don't lose the whole scrape
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
			#print('Succesfully scraped: '+song)
		except:
			print("Couldn't scrape: "+song)
		#sleep to not overrun server
		time.sleep(slept)
	return song_text


#scraping is now all done, have to do intial clean
def raw_clean(song_texts, scrape_artist):
	song_data = {}
	count_raw = 0
	count_clean = 0
	for song in song_texts:
		try:
			#sometimes artist is written incorrectly dur
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
			#before we append lyrics, want to clean them slightly further
			words = re.sub("([\(\[]).*?([\)\]])", "", lyrics)
			words = re.sub("\n","--",words)

			if artist not in song_data:
				song_data[artist] = {}
			if album not in song_data[artist]:
				song_data[artist][album] = {}
			song_data[artist][album][title] = words

			count_clean += 1
		except:
			#again, want to use try excepts for indivdual artist
			song_data['raw_song_'+str(count_raw)] = song
			count_raw += 1
	print(str(count_raw)+" songs cleaned raw")
	print(str(count_clean)+" songs cleaned clean")
	return song_data