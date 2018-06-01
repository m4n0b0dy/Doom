from rap_scrpr import *
#boolean tells it if its one of two style pages
artist_to_scrape = {'eminem':'http://www.ohhla.com/YFA_eminem.html',
                   'afroman':'http://ohhla.com/anonymous/afroman/',
                   '50_cent':'http://www.ohhla.com/YFA_50cent.html',
                   'odd_future':'http://ohhla.com/YFA_oddfuture.html',
                   'dr_octagon':'http://ohhla.com/YFA_koolkeith_two.html',
                   'dr_dre':'http://ohhla.com/YFA_drdre.html',
                   'blackalicious':'http://ohhla.com/anonymous/blackali/',
                   'anderson_paak':'http://ohhla.com/anonymous/and_paak/',
                   'aesop_rock':'http://ohhla.com/anonymous/aesoprck/'}
for art, page in artist_to_scrape.items():
    #latency timing of 1
    scraped_songs = raw_clean(song_scrape(song_links(page)), art)
    #back up scrape after clean
    with open('json_lyrics/'+art+'_raw.json', 'w') as outfile:
        json.dump(scraped_songs, outfile)
    print(art+'_raw.json made!')