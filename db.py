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




def insert_data(data, steamid):
    """
    Main function that calls insert functions
    """
    insert_friends(data, steamid)
    insert_friends_bans(data, steamid)
    insert_steam_stats(data, steamid)
    insert_faceit_stats(data, steamid)

 
def fetch_from_db(steamid):
    friends = get_banned_friends(steamid)
    faceit_stats = get_faceit_stats(steamid)
    steam_stats = get_steam_stats(steamid)
    return friends, faceit_stats, steam_stats


def get_banned_friends(steamid):
    # Lets also use dict for consistency with other fetch methods, list would be more natural
    data_dict = {}
    sql = """
            SELECT DISTINCT friends.user2, bans.vacban, bans.steamban, bans.banned_days_ago 
            FROM friends, bans
            WHERE friends.user2=bans.steamid
                AND friends.user1=:steamid
                AND (bans.vacban=True OR bans.steamban=True)
          """
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()
    banned_friends_list = [friend for friend in out]
    data_dict["banned_friends"] = banned_friends_list
    return data_dict

def get_faceit_stats(steamid):
    data_dict = {}
    sql = """
          SELECT faceit_level, faceit_name, country, kdr, n_matches, winrate, hs_ratio
          FROM faceitstats
          WHERE steamid = :steamid
          ORDER BY created_at
          LIMIT 1;
          """
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()[0]
    print("OUT", out)
    data_dict["faceit_level"] = out[0]
    data_dict["faceit_name"] = out[1]
    data_dict["country"] = out[2]
    data_dict["kdr"] = out[3]
    data_dict["n_matches"] = out[4]
    data_dict["winrate"] = out[5]
    data_dict["hs_ratio"] = out[6]
    return data_dict


def get_steam_stats(steamid):
    data_dict = {}
    sql = """
          SELECT hours_csgo, hours_steam, total_games
          FROM steamstats
          WHERE steamid = :steamid
          ORDER BY created_at
          LIMIT 1;
          """
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()[0]
    data_dict["hours_csgo"] = out[0]
    data_dict["hours_steam"] = out[1]
    data_dict["total_games"] = out[2]
    return data_dict


def insert_friends(data, steamid):
    for friend in data['Friends banned list']:
        friend_id = friend[0]
        sql = "INSERT INTO FRIENDS (user1, user2) VALUES (:user1, :user2)"
        db.session.execute(sql, {"user1": steamid, "user2":friend_id})
    db.session.commit()


def insert_friends_bans(data, steamid):
    """
    inserts 
    """

    for friend in data['Friends banned list']:

        steamid = friend[0]
        vacban = friend[1]
        gamebans = True if friend[2] > 1 else False
        days_banned_ago = friend[3]

        sql = "INSERT INTO bans (steamid, vacban, steamban, banned_days_ago) VALUES (:steamid, :vacban, :steamban, :banned_days_ago)"
        db.session.execute(sql, {"steamid": steamid,
                                "vacban":vacban,
                                "steamban":gamebans,
                                "banned_days_ago":days_banned_ago})
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
    

def insert_last_lookup(steamid):
    sql = """INSERT INTO lastlookup (steamid, hours_csgo, hours_steam, total_games)
             VALUES (:steamid, :hours_csgo, :hours_steam, :total_games)"""
    
    db.session.execute(sql, {"steamid": steamid,
                             "hours_csgo":hours_csgo,
                             "hours_steam": hours_steam,
                             "total_games": total_games
                             })
    db.session.commit()


if __name__ == "__main__":
    insert_friends_bans(76561198112024117, True, False, 12)