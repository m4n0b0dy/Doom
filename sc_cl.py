import json
import re
#import psycopg2 as pg2
from bs4 import BeautifulSoup
import urllib
import time

scrape_artist = 'MF_DOOM'
artist_page = 'http://ohhla.com/YFA_mfdoom.html'

page = urllib.request.urlopen(artist_page).read()
soup = BeautifulSoup(page, 'html.parser')

#find links to an artist's song
def song_links(muiscal_soup):
	count = 0
	song_list = []
	#finds all links
	for a in muiscal_soup.find_all('a'):
		#if they are a text link aka lyrics
		print(a)
		if '.txt">' in str(a):
			#get rid of front link
			lines = str(a).split('">')
			match = re.search(r'href=[\'"]?([^\'" >]+)', lines[0])
			#pull out link
			link = match.group(1)
			title = lines[1][:-4]
			#add it to our links
			song_list.append(link)
		#for testing just do 1
	print(song_list)
	return song_list


#scrape the links
def song_scrape(links, slept):
	song_text = []
	for song in links:
		#do this just in case so we don't lose the whole scrape
		try:
			#load and parse lytics page
			page = urllib.request.urlopen("http://ohhla.com/"+song).read()
			text = BeautifulSoup(page, 'html.parser')
			#can hit error cause sometimes pre isn't used
			try:
				lyrics_page = str(text.find_all('pre')[0])
			except:
				lyrics_page = str(text)
			#add text without all of the links	
			song_text.append(re.sub('<[^>]*>', '', lyrics_page))
			print('Succesfully scraped: '+song)
		except:
			print("Couldn't scrape: "+song)
	#sleep to not overrun server
	time.sleep(slept)
	return song_text


#scraping is now all done, have to do intial clean
def raw_clean(song_texts):
	song_data = {}
	song_data[scrape_artist] = []
	count = 0
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

			song_data[scrape_artist].append({'Title':title,'Album':album, 'Artist':artist, 'Lyrics':words})
		except:
			#again, want to use try excepts for indivdual artist
			song_data[scrape_artist].append({'Raw':song})
			count += 1
	print(str(count)+" songs cleaned raw")
	return song_data

scraped_songs = raw_clean(song_scrape(song_links(soup), .1))

#back up scrape after clean
with open(scrape_artist+'_raw.json', 'w') as outfile:
    json.dump(scraped_songs, outfile)