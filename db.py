from apicalls.api_calls import *
from flask import Flask
from flask import redirect ,render_template, request
import requests
from apicalls.api_calls import get_all_data
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


def insert_friends(input_id, friends_list):
    for friend in friends_list:
        sql = "INSERT INTO FRIENDS (user1, user2) VALUES (:user1, :user2)"
        db.session.execute(sql, {"user1": input_id, "user2":friend})
    db.session.commit()


def insert_bans(steamid, vacban, steamban, banned_days_ago):
    sql = "INSERT INTO bans (steamid, vacban, steamban, banned_days_ago) VALUES (:steamid, :vacban, :steamban, :banned_days_ago)"
    db.session.execute(sql, {"steamid": steamid,
                             "vacban":vacban,
                             "steamban":steamban,
                             "banned_days_ago":banned_days_ago})
    db.session.commit()

def insert_faceit_stats(steamid, vacban, steamban, banned_days_ago):
    sql = "INSERT INTO bans (steamid, vacban, steamban, banned_days_ago) VALUES (:steamid, :vacban, :steamban, :banned_days_ago)"
    db.session.execute(sql, {"steamid": steamid,
                             "vacban":vacban,
                             "steamban":steamban,
                             "banned_days_ago":banned_days_ago})
    db.session.commit()



def get_friends(steamid):
    sql = "SELECT user2 FROM friends WHERE user1 = (:steamid)"
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()
    return out


if __name__ == "__main__":
    insert_bans(76561198112024117, True, False, 12)