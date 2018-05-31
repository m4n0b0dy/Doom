import json
import nltk
import re
import psycopg2 as pg2

#simple cleaning
#def clean_lyrics(full_text):
#    words = re.sub("([\(\[]).*?([\)\]])", "", full_text)
#    words = re.sub("\n","----",words)
#    return words

#thinking about adding a table like primary artist where it's the main guy

#create the tables - will over write
def create_music_tables(conn, bypass = False):
	ans = 'y'
	if not bypass:
		ans = input('You sure you want to overwrite your tables? Type:"y"')
	if ans == 'y':
	    clean = '''DROP TABLE IF EXISTS artists, albums, songs'''
	    artists = '''CREATE TABLE artists
	                (artist_id SERIAL PRIMARY KEY,
	                artist_name TEXT NOT NULL UNIQUE,
	                artist_backg TEXT)'''
	    albums = '''CREATE TABLE albums
	                (album_id SERIAL PRIMARY KEY,
	                artist_id SERIAL
	                REFERENCES artists (artist_id)
	                ON UPDATE CASCADE ON DELETE CASCADE,
	                album_name TEXT NOT NULL,
	                album_sld SERIAL,
	                album_rtng SERIAL,
	                album_rev SERIAL,
	                UNIQUE (album_name, artist_id))'''
	    songs = '''CREATE TABLE songs
	                (song_id SERIAL PRIMARY KEY,
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
	                UNIQUE (song_name, album_id, artist_id))'''
	    #added unqiue stuff at the end because just uniquing song doesn't allow songs with the same name
	    cur = conn.cursor()
	    for command in [clean, artists, albums, songs]:
	        cur.execute(command)
	    cur.close()
	    conn.commit()
	else:
		print('be more careful next time!')

def add_songs(conn, art_name, art):
    art_add = '''INSERT INTO artists (artist_name) VALUES (%(art)s)
                    ON CONFLICT (artist_name) DO NOTHING''', {'art':art_name}
    alb_add = []
    song_add = []
    for alb_name, alb in art.items():
        add = '''INSERT INTO albums (album_name, artist_id) VALUES
                    (%(alb)s,
                    (SELECT artist_id FROM artists WHERE artist_name = %(art)s))
                    ON CONFLICT (album_name, artist_id) DO NOTHING''', {'art':art_name,'alb':alb_name}
        alb_add.append(add)
        for sng_name, sng in alb.items():
            add = '''WITH art_id AS (SELECT artist_id FROM artists WHERE artist_name = %(art)s)
                        INSERT INTO songs (song_name, song_lyrics, artist_id, album_id) VALUES
                        (%(sng)s, %(lyrcs)s, (SELECT artist_id FROM art_id),
                        (SELECT album_id FROM albums WHERE album_name = %(alb)s and artist_id IN (SELECT artist_id FROM art_id)))
                        ON CONFLICT (song_name, album_id, artist_id) DO NOTHING''', {'art':art_name,'alb':alb_name, 'sng':sng_name, 'lyrcs':sng}
            song_add.append(add)
    
    cur = conn.cursor()
    for command in [art_add] + alb_add + song_add:
        cur.execute(command[0],command[1])
    cur.close()
    conn.commit()

def basic_lyrc_pull(conn, art, alb=False, song=False):
    add = []
    if not song and not alb:
        add = [('''SELECT song_name, song_lyrics FROM songs
        JOIN artists ON songs.artist_id = artists.artist_id
        #could change this to like ('%Artist%') if you want to pull all containing artist name
        WHERE artists.artist_name = %(art)s''', {'art':art})]
    elif not song:
        add = [('''SELECT song_name, song_lyrics FROM songs
        JOIN artists ON songs.artist_id = artists.artist_id
        JOIN albums ON songs.album_id = albums.album_id
        WHERE artists.artist_name = %(art)s AND albums.album_name = %(alb)s''', {'art':art,'alb':alb})]
    else:
        for s in song:
            query = '''SELECT song_name, song_lyrics FROM songs
            JOIN artists ON songs.artist_id = artists.artist_id
            JOIN albums ON songs.album_id = albums.album_id
            WHERE artists.artist_name = %(art)s AND
            albums.album_name = %(alb)s AND
            song_name = %(sng)s''', {'art':art,'alb':alb, 'sng':s}
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
    return ret_dic