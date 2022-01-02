# This file interacts with the database outside of the app
# See create_db.py for interacting with the app with SQLAlchemy

import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
import app.pybracket as pybracket
import datetime
import json

conn = psycopg2.connect("dbname='tennis_bracket' user='postgres' host='localhost' password='{}'".format('password'))

cur = conn.cursor()

cur.execute("""
CREATE TABLE user_pass(
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("""
    CREATE TABLE tournaments(
        tournament_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        year INTEGER NOT NULL,
        start_time TIMESTAMPTZ NOT NULL,
        end_time TIMESTAMPTZ NOT NULL,
        points_per_round JSON NOT NULL,
        atplink TEXT,
        bracketsize INTEGER NOT NULL,
        surface TEXT,
        sets INTEGER,
        players JSON NOT NULL,
        elos JSON NOT NULL,
        results JSON
    );
""")

cur.execute("""
    CREATE TABLE brackets(
        bracket_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        tournament_id INTEGER NOT NULL,
        bracket JSON NOT NULL,
        CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user_pass(user_id),
        CONSTRAINT fk_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id)
    );
""")


# Add a user
usernames = ["Andres","Daniel","Felipe","Anamaria","Elo"]
for user in usernames:
    cur.execute("""
        INSERT INTO user_pass (username,password) 
            Values (%s,%s)
    """,
    (user,generate_password_hash("a"))
    )

# Add a tournament

## Load Wimbledon as an example for testing 
b = pybracket.Bracket()
b.loadFromFolder("../tennis-bracket/docs/Wimbledon 2021")

def playernames2indices(target_list,player_list):
    x = []
    for i in target_list:
        for j,player in enumerate(player_list):
            if i == player:
                x.append(j)
                break
            if (j==len(player_list)-1):
                x.append(-1)
                print('No match for ',i)
    return x

b.results = playernames2indices(b.results,b.players)
for i in b.brackets:
    b.brackets[i] = playernames2indices(b.brackets[i],b.players)
b.updateResults(scrape=False)

# change usernames to user ids in table_results
cur.execute("SELECT * FROM user_pass")
for i in cur.fetchall():
    print(i[0],": ",i[1])
b.table_results
user_list = [4,1,5,6,3,2]
b.table_results['user'] = user_list

# change usernames to user ids in brackets
dict_key_list = list(b.brackets.keys())
user_list = [1,2,5,3,6,4]
for i,j in enumerate(dict_key_list):
    b.brackets[user_list[i]] = b.brackets[j]

cur.execute("""
    INSERT INTO tournaments (
        name,
        year,
        start_time,
        end_time,
        points_per_round,
        atplink,
        bracketSize,
        surface,
        sets,
        players,
        elos,
        results)
    Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
""",
(
    "Wimbledon",
    2021,
    datetime.datetime(2021,6,30,11,0,0,tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
    datetime.datetime(2021,7,12,23,59,0,tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
    json.dumps(b.points_per_round),
    b.atplink,
    b.bracketSize,
    b.surface,
    5,
    json.dumps(b.players),
    json.dumps(b.elo),
    json.dumps({"results":b.results,"scores":b.scores,"losers":b.losers,"table_results":b.table_results})
))


# Add brackets
b.table_results['user']
user_list = [1,2,3,4,5,6]
cur.execute("SELECT tournament_id, name, year FROM tournaments")
cur.fetchall()
tournament_id = 1
for i in user_list:
    cur.execute("""
        INSERT INTO brackets (
            user_id,
            tournament_id,
            bracket
        )
        VALUES (%s,%s,%s);
    """,
    (
        i,
        tournament_id,
        json.dumps(b.brackets[i])
    ))

cur.execute("SELECT * FROM user_pass")
cur.fetchall()
cur.execute("DELETE FROM brackets WHERE tournament_id=2;")

cur.execute("DELETE FROM tournaments WHERE tournament_id = 2;")

cur.execute("SELECT tournament_id, name, results FROM tournaments WHERE name='Wimbledon';")
cur.fetchall()

conn.commit()

conn.rollback()

cur.close()
conn.close()