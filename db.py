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

def insert_faceit_stats(data, steamid):
    faceit_level = data["Faceit level"]
    faceit_name = data["Name on Faceit"]
    faceit_country = data["Country Code"]
    faceit_kdr = data["KDR"]
    faceit_matches = data["Total matches on Faceit"]
    faceit_winrate = data["Winrate"]
    faceit_hs_ratio = data["Headshot ratio"]

    sql = """INSERT INTO faceitstats (steamid, faceit_level, faceit_name, country, kdr, n_matches, winrate, hs_ratio)
             VALUES (:steamid, :faceit_level, :faceit_name, :country, :kdr, :n_matches, :winrate, :hs_ratio)"""

    db.session.execute(sql, {"steamid": steamid,
                             "faceit_level":faceit_level,
                             "faceit_name": faceit_name,
                             "country":faceit_country,
                             "kdr": faceit_kdr,
                             "n_matches":faceit_matches,
                             "winrate":faceit_winrate,
                             "hs_ratio":faceit_hs_ratio,
                             })
    db.session.commit()


def insert_steam_stats(data, steamid):
    hours_csgo = data["Hours of CSGO"]
    hours_steam = data["Total hours on Steam"]
    total_games = data["Total games on Steam"]

    sql = """INSERT INTO steamstats (steamid, hours_csgo, hours_steam, total_games)
             VALUES (:steamid, :hours_csgo, :hours_steam, :total_games)"""
    
    db.session.execute(sql, {"steamid": steamid,
                             "hours_csgo":hours_csgo,
                             "hours_steam": hours_steam,
                             "total_games": total_games
                             })
    db.session.commit()
    

def get_friends(steamid):
    sql = "SELECT user2 FROM friends WHERE user1 = (:steamid)"
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()
    return out


def insert_data(data, steamid):
    """
    Main function that calls insert functions
    """
    insert_faceit_stats(data, steamid)
    insert_steam_stats(data, steamid)


if __name__ == "__main__":
    insert_bans(76561198112024117, True, False, 12)