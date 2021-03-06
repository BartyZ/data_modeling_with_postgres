import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    - Reads data from a song file stored in filepath
    
    - Loads the data to the songs table using song_table_insert script from sql_queries
    
    - Loads the data to the artists table using artist_table_insert script from sql_queries
    """    
    
    # open song file
    df = pd.read_json(filepath, lines=True) 

    # insert song record
    selected_columns = df[["song_id", "title", "artist_id", "year", "duration"]]
    row_to_insert = selected_columns.values[0]
    song_data = song_data = row_to_insert.tolist()
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    selected_columns = df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]]
    row_to_insert = selected_columns.values[0]
    artist_data = row_to_insert.tolist()
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    - Reads data from a log file stored in filepath, filtering out all records except "page" = NextSong
    
    - Converts timestamp to datetime and calculate other columns for the time table
    
    - Loads the data to the time table using time_table_insert script from sql_queries
    
    - Loads the data to the users table using user_table_insert script from sql_queries
    
    - Loads the data to the songplays table using songplay_table_insert script from sql_queries
    """        
    # open log file
    df = pd.read_json(filepath, lines=True) 

    # filter by NextSong action
    df = df[df["page"]=="NextSong"]

    # convert timestamp column to datetime and calculate other date-columns
    df["timestamp"] = pd.to_datetime(df["ts"], unit='ms')
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["week"] = df["timestamp"].dt.week
    df["month"] = df["timestamp"].dt.month
    df["year"] = df["timestamp"].dt.year
    df["weekday"] = df["timestamp"].dt.weekday_name
    
    # insert time data records
    time_data = pd.concat([df["timestamp"], df["hour"], df["day"], df["week"], df["month"], df["year"], df["weekday"]], axis=1)
    column_labels = ['start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday']
    time_data.columns = column_labels
     
    time_df = time_data.drop_duplicates(subset=None, keep='first', inplace=False)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    # Duplicates are removed to minimize the amount of data to process
    user_df_withduplicates = df[["userId", "firstName", "lastName", "gender", "level"]]
    user_df = user_df_withduplicates.drop_duplicates(subset=None, keep='first', inplace=False)

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        selected_columns = df[["timestamp", "userId", "level", "sessionId", "location", "userAgent"]]
        row_to_insert = selected_columns.values[0]
        songplay_data = row_to_insert.tolist() 
        songplay_data.append(songid)
        songplay_data.append(artistid)
        
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    Reads all json files from the specified filepath, 
    applying func on each of them
    """     
    
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Connects to the database and processes files from 'data/song_data' and 'data/log_data' folders
    """     
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()