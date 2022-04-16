from apicalls.api_calls import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)


def insert_data(data, steamid):
    """
    Main function that calls smaller insert functions
    """
    insert_friends(data, steamid)
    insert_bans(data, steamid)
    insert_steam_stats(data, steamid)
    insert_faceit_stats(data, steamid)


def insert_friends(data, steamid):
    for friend in data['Friends banned list']:
        friend_id = friend[0]
        sql = "INSERT INTO FRIENDS (user1, user2) VALUES (:user1, :user2)"
        db.session.execute(sql, {"user1": steamid, "user2":friend_id})
    db.session.commit()


def insert_bans(data, steamid):
    """
    inserts both the player and friends bans
    """
    # Friends
    for friend in data['Friends banned list']:

        friend_id = friend[0]
        vacban = friend[1]
        gamebans = True if friend[2] > 1 else False
        days_banned_ago = friend[3]
        sql = "INSERT INTO bans (steamid, vacban, steamban, banned_days_ago) VALUES (:steamid, :vacban, :steamban, :banned_days_ago)"
        db.session.execute(sql, {"steamid": friend_id,
                                "vacban":vacban,
                                "steamban":gamebans,
                                "banned_days_ago":days_banned_ago,        
                                })
    db.session.commit()                               
    # Player
    gamebans = data["gamebans"]
    gameban = True if gamebans > 1 else False
    vacbans = data["n_vacs"]
    vacban = True if vacbans > 1 else False
    faceitban = data["Banned on Faceit"]
    days_banned_ago = data["ban_days_ago"]

    print("BANNED ON FACEIT:", faceitban)
    sql = "INSERT INTO bans (steamid, vacban, steamban, faceitban, banned_days_ago) VALUES (:steamid, :vacban, :steamban,:faceitban, :banned_days_ago)"
    db.session.execute(sql, {"steamid": steamid,
                            "vacban":vacban,
                            "steamban":gameban,
                            "faceitban":faceitban,
                            "banned_days_ago":days_banned_ago
                            })
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
    steam_name = data["steam_name"]
    hours_csgo = data["Hours of CSGO"]
    hours_steam = data["Total hours on Steam"]
    total_games = data["Total games on Steam"]

    sql = """INSERT INTO steamstats (steamid, steam_name, hours_csgo, hours_steam, total_games)
             VALUES (:steamid, :steam_name, :hours_csgo, :hours_steam, :total_games)"""
    
    db.session.execute(sql, {"steamid": steamid,
                            "steam_name": steam_name,
                             "hours_csgo":hours_csgo,
                             "hours_steam": hours_steam,
                             "total_games": total_games
                             })
    db.session.commit()