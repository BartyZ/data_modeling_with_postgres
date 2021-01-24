# Introduction

## Sparkify

***Sparkify*** means **FRESHNESS, ENERGY and JOY** - this is what we are!  

As Sparkify we have one goal: to strengthen every moment of your life! </br>
How do we do this? By accompanying you with the best-fit-music. Whenever you are happy or sad, moody or angry, or you just need to focus on your task - be yourself, and we will care about the noise!


## "Out Of Darkness" project

We decided to start the *Out Of Darkness* project to gain ~~any~~ better insight into our data. </br>
So far we were happy seeing billions of dollars flowing from subscribers to our account every month, but recently the flow seems to be decreasing. We have to check what is going on, but so far we are not able to analyse the data because of the way how it is stored.

**The aim of the project** is to create a database which is:
- easily accessible, 
- has a structure easy to understand, 
- can be analysed by standard SQL queries, </br>

so the analytics team can understand what songs users are listening to. 


### Starting point

Our data is stored as 2 sets of **json** files:

#### Log data
***Log_data*** files store all information we have about users and their sessions, including user's name and location, level of access, song and artist name, timestamp when the song was played etc. The fields available in every log_data file are:
- artist
- auth
- firstName
- gender
- itemInSession
- lastName
- length
- level
- location
- method
- page
- registration
- sessionId
- song
- status
- ts
- userAgent
- userId

The log_data files are partitioned by **year and month**, with a separate folder for each partition. 
For example, below we have pasted filepaths to two files in this dataset:
> log_data/**2018/11**/2018-11-12-events.json </br>
> log_data/**2018/11**/2018-11-13-events.json </br>


#### Song data
***Song_data*** files provide information about every single songs available in our service, along with some info about the artist. 
The following fields are available for each song:
- artist_id
- artist_latitude
- artist_location
- artist_longitude
- artist_name
- duration
- num_songs
- song_id
- title
- year

Each json file in the song_data dataset stores info about one song. The song_data files are partitioned by the first three letters of each song's track ID. 
For example, below we have pasted filepaths to two files in this dataset:
> song_data/**A/B/C**/TRABCEI128F424C983.json </br>
> song_data/**A/A/B**/TRAABJL12903CDCF1A.json </br>


# Project Details

## Technology

1. **Lucidchart** to build **ERD diagrams**. <br/> Functional and reliable tool to model our databse first, before we start coding anything. Lucidchart diagrams are not included in the project files.


2. **PostgreSQL** as a **RDBMS**. <br/> We decided to trust this well-known and battle-tested relational database management system. It is open-source and free, which is a huge advantage over the competitors!


3. **Python** as a tool to build **ETL processes**. <br/> It's very flexible programming language with hundreds of useful libraries, including a few to handle json files and to make working with PostgreSQL easy. Last but not least, we have a few ~~cheap~~ skilled Python developers in our company already!


4. **Power BI** as a **Business Intelligence** tool. <br/> In the Internet we saw a few dashboards built in this tool, they look just amazing and we want to have the same! But first things first - let's start from a database...


## Database schema

The database consists of **5 tables** organized into a **star schema**. <br/>
If you want to read more about star schema, please follow [this link](https://en.wikipedia.org/wiki/Star_schema).

### Fact table
*Table name:* ***songplays*** <br/>
*Fields:* **songplay_id, start_time, user_id, level, session_id, location, user_agent, song_id, artist_id** <br/>
*Datasource:* **log_data, song_data**

### Dimensions
*Table name:* ***users*** <br/>
*Fields:* **user_id, first_name, last_name, gender, level** <br/>
*Datasource:* **log_data**

*Table name:* ***songs*** <br/>
*Fields:* **song_id, title, artist_id, year, duration** <br/>
*Datasource:* **song_data**

*Table name:* ***artists*** <br/>
*Fields:* **artist_id, name, location, latitude, longitude** <br/>
*Datasource:* **song_data**

*Table name:* ***time*** <br/>
*Fields:* **start_time, hour, day, week, month, year, weekday** <br/>
*Datasource:* **log_data**


## Files in repository
1. **README.md** - you probably found this file already and you know what is inside...
2. **Launcher.ipynb** - use it to run other scripts to create the database and run ETL process.
3. **create_tables.py** - contains frame code to create database with appropriate tables
4. **etl.py** - ETL process to read data from json files, transform it and load into the database tables
5. **sql_queries.py** - SQL queries used by *create_tables.py* and *etl.py*.
6. **test.ipynb** - a Jupyter Notebook file you can use to test if youre database was created and uploaded with data successfully
7. **etl.ipynb** - a Jupyter Notebook file used during the development process of *etl.py*. It loads database tables with just few rows. It's not used anymore, but can be useful for further etl development.



## How to run the ETL process
To create the database and load it with data, please use the ***Launcher.ipynb*** file.


## Example queries 
Please find below some SQL queries which you may find useful to start analysing data.

#### Complete info about a songplay record (joining all tables)
>SELECT *  <br/>
FROM songplays sp   
    INNER JOIN users u ON sp.user_id = u.user_id  
    INNER JOIN songs s ON sp.song_id = s.song_id  
    INNER JOIN artists a ON sp.artist_id = a.artist_id  
    INNER JOIN time t ON sp.start_time = t.start_time  
    
#### Total time spent by user on listening music in the selected year & month
>SELECT u.user_id, sum(s.duration) as total_songs_duration  
FROM songplays sp   
    INNER JOIN users u ON sp.user_id = u.user_id  
    INNER JOIN songs s ON sp.song_id = s.song_id   
    INNER JOIN time t ON sp.start_time = t.start_time  
WHERE t.year = **(selected year)**   
ABD t.month = **(selected month)**   
GROUP BY u.user_id
    
#### No. songs in the database for the selected artist
>SELECT a.name, count(s.song_id) as total_songs  
FROM songs s  
    INNER JOIN artists a ON s.artist_id = a.artist_id  
WHERE a.name = **(artist's name)**   
GROUP BY a.name

#### Songs no one wants to listen (e.g. songs not played at all)
>SELECT s.title, a.name  
FROM songs s  
    INNER JOIN artists a ON s.artist_id = a.artist_id  
    LEFT JOIN songplays sp ON s.song_id = sp.song_id  
WHERE sp.song_id IS NULL



# Further development ideas

### Naming convention
We could rename tables by adding prefixes, to make it clear which of them are facts/dimensions. <br/>
songplays -> **fact**_songplays  
users -> **dim**_users  
songs -> **dim**_songs  
artists -> **dim**_artists  
time -> **dim**_time  


### REFERENCES and load order
When we work with a complete dataset (not just a subset) we could add REFERENCES to foreing key definitions in the create_table part of the sql_queries.py.
E.g. for the songplays CREATE_TABLE script, we could add what is **bold** below:
>CREATE TABLE IF NOT EXISTS songplays (  
    songplay_id SERIAL PRIMARY KEY,  <br/>
    start_time timestamp **REFERENCES time(start_time)**,  <br/>
    user_id int **REFERENCES users(user_id)**,  <br/>
    level varchar,  <br/>
    song_id varchar **REFERENCES songs(song_id)**,  <br/>
    artist_id varchar **REFERENCES artists(artist_id)**,  <br/>
    session_id int,  <br/>
    location varchar,  <br/>
    user_agent varchar  
    );
    
It would provide additional quality check for these keys. We would just have to ensure that **the dimension tables are loaded first** in the ETL process, as all keys have to already exist when we attempt to load songplays fact table.