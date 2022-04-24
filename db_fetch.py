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


def fetch_from_db(steamid):
    """
    Main fetch function, calls smaller fetches
    """
    friends = get_banned_friends(steamid)
    faceit_stats = get_faceit_stats(steamid)
    steam_stats = get_steam_stats(steamid)
    user_bans = get_user_bans(steamid)
    return user_bans, friends, faceit_stats, steam_stats


def get_user_bans(steamid):
    data_dict = {}
    sql = """
            SELECT vacban, steamban, faceitban, banned_days_ago
            FROM bans
            WHERE steamid=:steamid
            ORDER BY banned_days_ago, created_at
          """
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()[0]
    data_dict["Vacban"] = out[0]
    data_dict["Gameban"] = out[1]
    data_dict["Faceitban"] = out[2]
    data_dict["Days since ban"] = out[3]
    return data_dict

def get_banned_friends(steamid):
    data_dict = {}
    sql = """
            SELECT DISTINCT friends.user2, bans.vacban, bans.steamban, bans.banned_days_ago 
            FROM friends, bans
            WHERE friends.user2=bans.steamid
                AND friends.user1=:steamid
                AND (bans.vacban=True OR bans.steamban=True)
            ORDER BY bans.banned_days_ago
          """
    result = db.session.execute(sql, {"steamid": steamid})
    out = result.fetchall()
    n_banned_friends = len(out)

    data_dict["ID"] = []
    data_dict["Vacban"] = []
    data_dict["Gameban"] = []
    data_dict["Days_ago"] = []
    for friend in out:
        data_dict["ID"].append(friend[0])
        data_dict["Vacban"].append(friend[1])
        data_dict["Gameban"].append(friend[2])
        data_dict["Days_ago"].append(friend[3])

    # Lets also get the total number of friends
    sql = """
            SELECT COUNT(DISTINCT friends.user2) 
            FROM friends 
            WHERE friends.user1=:steamid
        """
    result = db.session.execute(sql, {"steamid": steamid})
    total_firends = result.fetchall()

    return data_dict, total_firends, n_banned_friends

def get_faceit_stats(steamid):
    data_dict = {}
    sql = """
          SELECT faceit_level, faceit_name, country, kdr, n_matches, winrate, hs_ratio
          FROM faceitstats
          WHERE steamid = :steamid
          ORDER BY created_at
          LIMIT 1;
          """
    result = db.session.execute(sql, {"steamid": steamid}).fetchall()
    if len(result) > 0:
        data_list = result[0]
        data_dict["Faceit Level"] = data_list[0]
        data_dict["Faceit Nickname"] = data_list[1]
        data_dict["Country"] = data_list[2]
        data_dict["KDR"] = data_list[3]
        data_dict["Number of Matches"] = data_list[4]
        data_dict["Winrate"] = data_list[5]
        data_dict["Headshot ratio"] = data_list[6]
    else:
        data_dict["Faceit Level"] = None
        data_dict["Faceit Nickname"] = None
        data_dict["Country"] = None
        data_dict["KDR"] = None
        data_dict["Number of Matches"] = None
        data_dict["Winrate"] = None
        data_dict["Headshot ratio"] = None
    return data_dict


def get_steam_stats(steamid):
    data_dict = {}
    sql = """
          SELECT steam_name, hours_csgo, hours_steam, total_games
          FROM steamstats
          WHERE steamid = :steamid
          ORDER BY created_at DESC
          LIMIT 1
          """

    result = db.session.execute(sql, {"steamid": steamid}).fetchall()
    print(result)
    if len(result) > 0:
        data_list = result[0]
        data_dict["Steam name"] = data_list[0]
        data_dict["Hours of CSGO"] = data_list[1]
        data_dict["Hours Total on Steam"] = data_list[2]
        data_dict["Total number of games"] = data_list[3]
    return data_dict