from rap_db import *
import psycopg2 as pg2
import psycopg2.extras
import re
from nltk.corpus import cmudict
from difflib import get_close_matches
CMU_DICT = cmudict.dict()
CMU_KEYS = set(CMU_DICT.keys())


estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
cur = estconn.cursor()
cur.execute('''SELECT LOWER(song_lyrics) FROM songs;''')
query = cur.fetchall()
_all_words = set()

LYRIC_SYL = {}
#want all rappers listed and any rapper in list of rappers
for lyrc in query:
	text = lyrc[0]
	#same splitting technique later used in verse
	text = re.sub('[^0-9a-zA-Z\'\-]+', ' ', text)
	text = text.split(' ')
	_all_words = _all_words|set(text)
_all_words = _all_words-{'',"'"}

#this is what takes a chunk of time
c = 0
for word in _all_words:
	if c % 1000 == 0 and c != 0:
		print(c)
		art_save({'LYRIC_SYLBLS':LYRIC_SYL})
	c+=1
	mtch = word
	if mtch not in CMU_KEYS:
		mtch = get_close_matches(word, CMU_KEYS)
	if mtch:
		try:
			LYRIC_SYL[word] = CMU_DICT[mtch[0]]
		except:
			print(mtch[0])
art_save({'LYRIC_SYLBLS':LYRIC_SYL})