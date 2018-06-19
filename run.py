from rap_scrpr import *
from rap_db import *

estconn = pg2.connect(database='rap_songs', user='keenan', host='localhost', password='keenan')
new_artists = scrape_multi_artists(estconn, [])
bulk_load(estconn, new_artists)