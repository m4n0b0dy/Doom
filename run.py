import RAP_MASTER_LIB
from rap_scrpr import *
from rap_db import *
from rap_clean_w_word import*
from rap_viz_wout_word import *

#art_to_db = []
estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
#new_artists = scrape_multi_artists(estconn, art_to_db)
#bulk_load(estconn, new_artists)

make_artists = ['Del', 'Chance', 'Doom', 'Earl']
#not working, why??/
art_save(dict(zip(make_artists, construct_artists(estconn, art_list = make_artists))))