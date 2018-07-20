import json
import psycopg2 as pg2
import psycopg2.extras
import pickle as pic
from os import listdir
from os import path
from os.path import isfile, join

#create the tables - will over write any data there
def create_music_tables(conn, bypass = False):
    ans = 'y'
    if not bypass:
        ans = input('You sure you want to overwrite your tables? Type:"y"')
    if ans == 'y':
        clean = '''DROP TABLE IF EXISTS base_artists, artists, albums, songs;'''
        base_artists = '''CREATE TABLE base_artists 
        (base_artist_id SERIAL PRIMARY KEY,
        base_artist_name TEXT NOT NULL UNIQUE,
        base_artist_backg TEXT);'''

        artists = '''CREATE TABLE artists
        (artist_id SERIAL PRIMARY KEY,
        artist_name TEXT NOT NULL UNIQUE,
        base_artist_id SERIAL
        REFERENCES base_artists (base_artist_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        UNIQUE (artist_name, base_artist_id));'''

        albums = '''CREATE TABLE albums
        (album_id SERIAL PRIMARY KEY,
        base_artist_id SERIAL
        REFERENCES base_artists (base_artist_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        artist_id SERIAL
        REFERENCES artists (artist_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        album_name TEXT NOT NULL,
        album_sld SERIAL,
        album_rtng SERIAL,
        album_rev SERIAL,
        UNIQUE (album_name, artist_id, base_artist_id));'''

        songs = '''CREATE TABLE songs
        (song_id SERIAL PRIMARY KEY,
        base_artist_id SERIAL
        REFERENCES base_artists (base_artist_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        artist_id SERIAL
        REFERENCES artists (artist_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        album_id SERIAL
        REFERENCES albums (album_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
        song_name TEXT NOT NULL,
        song_lyrics TEXT NOT NULL,
        song_wrd_len SERIAL,
        song_time_len SERIAL,
        UNIQUE (song_name, album_id, artist_id, base_artist_id));'''
        #added unqiue stuff at the end because just uniquing song doesn't allow songs with the same name
        cur = conn.cursor()
        for command in [clean, base_artists, artists, albums, songs]:
            cur.execute(command)
        cur.close()
        conn.commit()
    else:
        print('be more careful next time!')
#add base artist aka what was used in pull - not used later
def add_base(conn, base_art_name):
    base_art_add = '''INSERT INTO base_artists (base_artist_name) VALUES (%(base_art)s)
                    ON CONFLICT (base_artist_name) DO NOTHING;''', {'base_art':base_art_name}
    cur = conn.cursor()
    cur.execute(base_art_add[0], base_art_add[1])
    cur.close()
    conn.commit()

#so an issue here is when another artist that is featured with an artist that has already been loaded is loaded,
#it tries to load that base ID but finds that there's two base artist names for that one artist name used in query

#add to database meta stats when you have em
def add_songs(conn, base_art_name, art_name, art):
    #add or ignore artist
    art_add = '''INSERT INTO artists (artist_name, base_artist_id) VALUES (%(art)s,
                (SELECT base_artist_id FROM base_artists WHERE base_artist_name = %(base_art)s))
                ON CONFLICT (artist_name) DO NOTHING;''', {'base_art':base_art_name, 'art':art_name}
    alb_add = []
    song_add = []
    for alb_name, alb in art.items():
        #add or ignore album
        add = '''INSERT INTO albums (album_name, base_artist_id, artist_id) VALUES
                    (%(alb)s,
                    (SELECT base_artist_id FROM artists WHERE artist_name = %(art)s),
                    (SELECT artist_id FROM artists WHERE artist_name = %(art)s))
                    ON CONFLICT (album_name, artist_id, base_artist_id) DO NOTHING;''', {'art':art_name,'alb':alb_name}
        alb_add.append(add)
        #add a song
        #think this can be tightend up, nbd for now but could be faster/cleaner with multi varaible assignment
        for sng_name, sng in alb.items():
            add = '''WITH base_art_id AS (SELECT base_artist_id FROM artists WHERE artist_name = %(art)s),
                    art_id AS (SELECT artist_id FROM artists WHERE artist_name = %(art)s)
                    INSERT INTO songs (song_name, song_lyrics, base_artist_id, artist_id, album_id) VALUES
                    (%(sng)s, %(lyrcs)s,
                    (SELECT base_artist_id FROM base_art_id),
                    (SELECT artist_id FROM art_id),
                    (SELECT album_id FROM albums WHERE album_name = %(alb)s
                    and base_artist_id IN (SELECT base_artist_id FROM base_art_id)
                    and artist_id IN (SELECT artist_id FROM art_id)))
                    ON CONFLICT (song_name, album_id, artist_id, base_artist_id) DO NOTHING;''', {'art':art_name,'alb':alb_name, 'sng':sng_name, 'lyrcs':sng}
            song_add.append(add)
    cur = conn.cursor()
    for command in [art_add] + alb_add + song_add:
        cur.execute(command[0],command[1])
    cur.close()
    conn.commit()

#this one is faster, only does one song at a time
#also only returns artist to song to lyrics dic rather than artist to album to song to lyrics
def percise_pull(conn, art, alb=False, song=False):
    add = []
    if not song and not alb:
        add = [('''SELECT song_name, song_lyrics FROM songs
        JOIN artists ON songs.artist_id = artists.artist_id
        WHERE artists.artist_name = %(art)s''', {'art':art})]
    elif not song:
        add = [('''SELECT song_name, song_lyrics FROM songs
        JOIN artists ON songs.artist_id = artists.artist_id
        JOIN albums ON songs.album_id = albums.album_id
        WHERE artists.artist_name = %(art)s AND albums.album_name = %(alb)s;''', {'art':art,'alb':alb})]
    else:
        for s in song:
            query = ('''SELECT song_name, song_lyrics FROM songs
            JOIN artists ON songs.artist_id = artists.artist_id
            JOIN albums ON songs.album_id = albums.album_id
            WHERE artists.artist_name = %(art)s AND
            albums.album_name = %(alb)s AND
            song_name = %(sng)s;''', {'art':art,'alb':alb, 'sng':s})
            add.append(query)
        
    cur = conn.cursor()
    quer = []
    for command in add:
        cur.execute(command[0],command[1])
        quer = cur.fetchall()
    cur.close()
    ret_dic = {}
    for qu in quer:
        ret_dic[qu[0]] = qu[1]
    full_ret_dic = {art:ret_dic}
    return full_ret_dic

def update_art_dic(art_dic, query, base_artist, use_ind_artists):
    #determines if we group by main artist or ind artists
    if use_ind_artists:
        artist_name_q = query['artist_name']
    else:
        artist_name_q = base_artist

    album_name_q = query['album_name']
    song_name_q = query['song_name']
    song_lyrics_q = query['song_lyrics']
    #if artist is there, use an update
    if artist_name_q in art_dic.keys():
        #all albs already there
        albs = art_dic[artist_name_q]
        #if alb already there, just add song
        if album_name_q in albs.keys():
            albs[album_name_q][song_name_q] = song_lyrics_q
        else:
            #otherwise add album name with song
            albs[album_name_q] = {song_name_q:song_lyrics_q}
        #update the artist dic with updated album
        art_dic[artist_name_q].update(albs)
    else:
        #if there artist isn't there, create artist, with alb and song
        art_dic[artist_name_q] = {album_name_q:{song_name_q:song_lyrics_q}}
    return art_dic

#this one is easier/more general but slower than first
#i map using the db artist name or base artist. It feeds into update art dic each song find
def adv_pull(conn, artist_list = [''], album_list = [''], song_list = [''], use_ind_artists=False):
    #special way of pulling that returns dict
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    queries = {}
    for art in artist_list:
        art_queries = {}
        for alb in album_list:
            for sng in song_list:
                #trys every artist, with every album and every song, if pull finds something runs update art dic
                #I use '' as a placeholder as it will still trigger for loop but won't filter
                song_pull = '''SELECT artist_name, album_name, song_name, song_lyrics FROM songs
                        JOIN artists ON artists.artist_id = songs.artist_id
                        JOIN albums ON albums.album_id = songs.album_id
                        WHERE lower(artist_name) LIKE '%'''+art.lower()+'''%' AND
                        lower(album_name) LIKE '%'''+alb.lower()+'''%' AND
                        lower(song_name) LIKE '%'''+sng.lower()+'''%';'''
                cur.execute(song_pull)
                query = cur.fetchall()
                for q in query:
                    art_queries = update_art_dic(art_queries, q, art, use_ind_artists)
        queries[art] = art_queries
    return queries

def pull_link_from_art(conn, artist_name):
    cur = conn.cursor()
    cur.execute('''SELECT artist_link from all_artist_names WHERE lower(artist_nm) = %(art)s''', {'art':artist_name.lower()})
    return 'http://ohhla.com/'+cur.fetchone()[0]

#function to load everything into db quickly
def bulk_load(conn, new_eds = []):
    if not new_eds:
        new_eds = [f for f in listdir('json_lyrics/') if path.isfile(join('json_lyrics/', f))]
    for rw_new in new_eds:
        new = rw_new.replace(' ', '_').lower()
        songs = json.load(open('json_lyrics/'+new))
        art_name = new.replace("_raw.json","")
        add_base(conn, art_name)
        for name, works in songs.items():
            if 'raw_song_' not in name:
                add_songs(conn, art_name, name, works)
        print(new+" added!")

#two quick and easy functions for loading my artist files
def art_save(arts):
    for nm, aobj in arts.items():
        with open('art_objs/%s.pkl'%nm, 'wb') as output:
            pic.dump(aobj, output, pic.HIGHEST_PROTOCOL)
            print('Saved %s!'%nm)

def art_load(nms = set()):
	ret_dic = {}
	if not nms:
		nms = set([f[:-4] for f in listdir('art_objs/') if isfile(join('art_objs/', f))])-{'COMPLETE_RAPPERS'}
	for nm in nms:
		with open('art_objs/%s.pkl'%nm, 'rb') as incoming:
			ret_dic[nm] = pic.load(incoming)
	return ret_dic