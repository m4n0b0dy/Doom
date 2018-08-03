import RAP_MASTER_LIB
from rap_scrpr import *
from rap_db import *
from rap_clean import*
from rap_viz import *

#art_to_db = []
estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
#new_artists = scrape_multi_artists(estconn, art_to_db)
#bulk_load(estconn, new_artists)
#maybe 1.5 hours
make_artists = ['Del', 'Chance', 'Doom', 'Earl', 'Mos Def', 'Talib Kweli', 'Danny Brown', 'Denzel Curry']
art_save(dict(zip(make_artists, construct_artists(estconn, art_list = make_artists))))