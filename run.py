from rap_scrpr import *
#boolean tells it if its one of two style pages
artist_to_scrape = {'eminem':('http://www.ohhla.com/YFA_eminem.html', False),
                   'mf_doom':('http://www.ohhla.com/YFA_mfdoom.html', False),
                   '50_cent':('http://www.ohhla.com/YFA_50cent.html', False),
                   'odd_future':('http://ohhla.com/YFA_oddfuture.html', False)}
for art, page in artist_to_scrape.items():
    #latency timing of 1
    scraped_songs = raw_clean(song_scrape(song_links(page[0], page[1])), art)
    #back up scrape after clean
    with open('json_lyrics/'+art+'_raw.json', 'w') as outfile:
        json.dump(scraped_songs, outfile)
    print(art+'_raw.json made!')