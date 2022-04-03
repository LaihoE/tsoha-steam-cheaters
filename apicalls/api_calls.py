import math
import os
import time
from threading import Thread
import pandas as pd
import requests
import csv
import pickle

key = os.environ['SteamKey']
faceit_key = os.environ['FaceitKey']


def convert_steamid_to_faceit_id(steamid):
    try:
        x = requests.get(f'https://api.faceit.com/search/v1/?limit=3&query={steamid}').json()
        faceit_id = x['payload']['players']['results'][0]['id']
        return faceit_id
    except Exception as e:
        return None


def check_steam_ban(steamid):
    response = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={key}&steamids={steamid}')
    print(response)
    response = response.json()
    print(response)
    for player in response['players']:
        sid = int(player["SteamId"])
        vacbans = bool(player["VACBanned"])
        gamebans = int(player["NumberOfGameBans"])
        n_vacs = int(player["NumberOfVACBans"])
        ban_days_ago = int(player["DaysSinceLastBan"])

    return sid, vacbans, gamebans, n_vacs, ban_days_ago


def get_percentage_of_friends_banned(steamid):
    try:
        # Get all friends
        friends_list = []
        response = requests.get(
            f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={steamid}&relationship=friend")
        print(response)
        response = response.json()

        all_friends = response['friendslist']['friends']
        for friend in all_friends:
            friends_list.append(int(friend['steamid']))

        # Check friends for bans
        banned_friends_list = []
        for i in range(math.ceil(len(friends_list) / 100)):
            slice_of_ids = friends_list[i * 100: i * 100 + 100]
            response = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={key}&steamids={slice_of_ids}')
            print(response)
            response = response.json()
            for player in response['players']:
                sid = int(player["SteamId"])
                vacbans = bool(player["VACBanned"])
                gamebans = int(player["NumberOfGameBans"])
                banned_friends_list.append((sid, vacbans, gamebans))

        # Sum all bans
        # If vac ban or game ban then True
        # List is of shape [(steamid, vacbanned, total_game_bans)...]
        return round(100 * sum([True if x[1] or x[2] > 0 else False for x in banned_friends_list]) / len(banned_friends_list),2)

    except Exception as e:
        return None


def get_friends_list_from_id(steamid):
    """
    Returns a list of ids: the users friends
    """
    try:
        friends_list = []
        response = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={steamid}&relationship=friend")
        print(response)
        response = response.json()
        response_friends = response['friendslist']['friends']
        for friend in response_friends:
            friends_list.append(int(friend['steamid']))
        return friends_list
    except Exception as e:
        return None


def get_faceit_banned_and_skill_level(steamid):
    try:
        x = requests.get(f'https://api.faceit.com/search/v1/?limit=3&query={steamid}').json()
        status = x['payload']['players']['results'][0]['status']
        skill = x['payload']['players']['results'][0]['games'][0]['skill_level']

        if status == 'BANNED':
            status = True
        else:
            status = False

        return status, skill
    except Exception as e:
        return None, None


def get_faceit_ingame_stats(steamid):
    try:
        faceit_id = convert_steamid_to_faceit_id(steamid)
        x = requests.get(f'https://open.faceit.com/data/v4/players/{faceit_id}/stats/csgo', headers={"Authorization": f"Bearer {faceit_key}"}).json()
        all_stats = x['lifetime']

        kdr = all_stats['Average K/D Ratio']
        total_matches = all_stats['Matches']
        winrate = all_stats['Win Rate %']
        headshot_ratio = all_stats['Average Headshots %']
        return kdr, total_matches, winrate, headshot_ratio
    except Exception as e:
        return None


def get_total_hours_of_csgo(steamid):
    try:
        x = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&format=json').json()
        games = x['response']['games']
        minutes_of_csgo = 0
        for game in games:
            # 730 is appid for csgo, also notice playtime is measured in minutes but we only care about hours
            if game['appid'] == 730:
                minutes_of_csgo = int(game['playtime_forever'])
        return int(minutes_of_csgo // 60)
    except Exception as e:
        return None


def get_total_hours_on_steam(steamid):
    try:
        x = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&format=json').json()
        total_playtime = 0
        games = x['response']['games']
        for game in games:
            total_playtime += int(game['playtime_forever'])
        return total_playtime // 60
    except Exception as e:
        return None


def get_total_number_of_games_steam(steamid):
    try:
        x = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&format=json').json()
        return len(x['response']['games'])
    except Exception as e:
        return None

def get_account_creation_time(steamid):
    data = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={steamid}')
    data = data.json()
    return data['response']['players'][0]['timecreated']


def get_faceit_high_level_info(steamid):
    try:
        faceit_id = convert_steamid_to_faceit_id(steamid)
        x = requests.get(f"https://open.faceit.com/data/v4/players/{faceit_id}", headers={"Authorization": f"Bearer {faceit_key}"}).json()

        nickname = x['nickname']
        csgo_data = x['games']['csgo']
        country = x['country']
        region = csgo_data['region']
        skill_level = csgo_data['skill_level']
        faceit_elo = csgo_data['faceit_elo']
        return nickname, country, region, skill_level, faceit_elo
    except Exception as e:
        return None

def get_inventory_value(steamid):
    inventory_value = 0

    # PLACEHOLDER SOLUTION
    with open('itemprices.pkl', "rb") as f:
        prices = pickle.load(f)
    try:
        item_list = []
        data = requests.get(f'https://steamcommunity.com/inventory/{steamid}/730/2').json()
        total_items = data["descriptions"]
        for item in total_items:
            item_list.append(item['market_hash_name'])

        for item in item_list:
            if item in prices:
                inventory_value += prices[item]
        return inventory_value
    except Exception as e:
        print(e)


# Custom Thread class with a return value
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def get_all_data(steamid):
    
    """
    MAYBE ASYNC WOULD OF BEEN BETTER but oh well...

    Super ugly multithreading solution, couldn't really find anything clean.
    Cuts runtime by around 5x.
    Using a custom Threading class that allows return values.
    See: https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
    """
    
    output = {}
    t1 = ThreadWithReturnValue(target=get_inventory_value, args=(steamid,))
    t2 = ThreadWithReturnValue(target=get_faceit_banned_and_skill_level, args=(steamid,))
    t3 = ThreadWithReturnValue(target=get_faceit_high_level_info, args=(steamid,))
    t4 = ThreadWithReturnValue(target=get_percentage_of_friends_banned, args=(steamid,))
    t5 = ThreadWithReturnValue(target=get_faceit_ingame_stats, args=(steamid,))
    t6 = ThreadWithReturnValue(target=get_total_hours_of_csgo, args=(steamid,))
    t7 = ThreadWithReturnValue(target=get_total_hours_on_steam, args=(steamid,))
    t8 = ThreadWithReturnValue(target=get_total_number_of_games_steam, args=(steamid,))

    threads = [t1, t2, t3, t4, t5, t6, t7, t8]
    temp_output = []
    for t in threads:
        t.start()
    for t in threads:
        # now the .join returns the value
        temp_output.append(t.join())

    output["Inventory value"] = 'tba' #temp_output[0]
    output["Banned on Faceit"] = temp_output[1][0]
    output["Faceit level"] = temp_output[1][1]

    output["Name on Faceit"] = temp_output[2][0]
    output["Country Code"] = temp_output[2][1]
    output["Region"] = temp_output[2][2]

    output["Friends banned percentage"] = temp_output[3]

    output["KDR"] = temp_output[4][0]
    output["Total matches on Faceit"] = temp_output[4][1]
    output["Winrate"] = temp_output[4][2]
    output["Headshot ratio"] = temp_output[4][3]

    output["Hours of CSGO"] = temp_output[5]
    output["Total hours on Steam"] = temp_output[6]
    output["Total games on Steam"] = temp_output[7]
    return output