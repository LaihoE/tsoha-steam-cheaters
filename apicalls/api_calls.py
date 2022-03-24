import math
import os
import time
from threading import Thread
import requests
import csv
import pickle

key = os.environ['steam_key']
faceit_key = os.environ['faceit_key']


def convert_steamid_to_faceit_id(steamid):
    try:
        x = requests.get(f'https://api.faceit.com/search/v1/?limit=3&query={steamid}').json()
        faceit_id = x['payload']['players']['results'][0]['id']
        return faceit_id
    except Exception as e:
        return None


def get_percentage_of_friends_banned(steamid):
    try:
        # Get all friends
        friends_list = []
        response = requests.get(
            f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={steamid}&relationship=friend").json()
        all_friends = response['friendslist']['friends']
        for friend in all_friends:
            friends_list.append(int(friend['steamid']))

        # Check friends for bans
        banned_friends_list = []
        for i in range(math.ceil(len(friends_list) / 100)):
            slice_of_ids = friends_list[i * 100: i * 100 + 100]
            response = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={key}&steamids={slice_of_ids}').json()
            for player in response['players']:
                sid = int(player["SteamId"])
                vacbans = bool(player["VACBanned"])
                gamebans = int(player["NumberOfGameBans"])
                banned_friends_list.append((sid, vacbans, gamebans))

        # Sum all bans
        # If vac ban or game ban then True
        # List is of shape [(steamid, vacbanned, total_game_bans)...]
        return sum([True if x[1] or x[2] > 0 else False for x in banned_friends_list]) / len(banned_friends_list)

    except Exception as e:
        return None




def get_friends_list_from_id(steamid):
    """
    Returns a list of ids: the users friends
    """
    try:
        friends_list = []
        response = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={key}&steamid={steamid}&relationship=friend").json()
        response_friends = response['friendslist']['friends']
        for friend in response_friends:
            friends_list.append(int(friend['steamid']))
        return friends_list
    except Exception as e:
        return None


def get_faceit_banned_and_skill_stats(steamid):
    try:
        x = requests.get(f'https://api.faceit.com/search/v1/?limit=3&query={steamid}').json()
        nickname = x['payload']['players']['results'][0]['nickname']
        x = requests.get(f"https://open.faceit.com/data/v4/search/players?nickname={nickname}&offset=0&limit=20",
                         headers={"Authorization": f"Bearer {faceit_key}"}).json()
        status = x['items'][0]['status']
        verified = x['items'][0]['verified']
        skill = x['items'][0]['games'][0]['skill_level']
        return status, verified, skill
    except Exception as e:
        return None


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

    item_list = []
    data = requests.get(f'https://steamcommunity.com/inventory/{steamid}/730/2').json()
    total_items = data["descriptions"]
    for item in total_items:
        item_list.append(item['market_hash_name'])

    for item in item_list:
        if item in prices:
            inventory_value += prices[item]
    return inventory_value


def create_headers(path):
    with open(f'{path}','w',newline='\n')as f:
        thewriter = csv.writer(f)
        thewriter.writerow(["vac","gameban","faceit_ban","faceit_level", "ban_percentage", "total_games", "steam_hours",
                            "csgo_hours", "kdr", "total_matches", "winrate", "headshot_ratio"])

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


def trust_checker(sid):
    output = []
    # Super ugly multithreading solution, couldn't really find anything clean.
    # Cuts runtime by around 5x.
    # Using a custom Threading class that allows return values.
    # See: https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

    t1 = ThreadWithReturnValue(target=get_inventory_value, args=(sid,))
    t2 = ThreadWithReturnValue(target=get_faceit_banned_and_skill_stats, args=(sid,))
    t3 = ThreadWithReturnValue(target=get_faceit_high_level_info, args=(sid,))
    t4 = ThreadWithReturnValue(target=get_percentage_of_friends_banned, args=(sid,))
    t5 = ThreadWithReturnValue(target=get_faceit_ingame_stats, args=(sid,))
    t6 = ThreadWithReturnValue(target=get_total_hours_of_csgo, args=(sid,))
    t7 = ThreadWithReturnValue(target=get_total_hours_on_steam, args=(sid,))
    t8 = ThreadWithReturnValue(target=get_total_number_of_games_steam, args=(sid,))

    threads = [t1, t2, t3, t4, t5, t6, t7, t8]
    for t in threads:
        t.start()
    for t in threads:
        # now the .join returns the value
        output.append(t.join())
    return output


if __name__ == "__main__":
    steamid = 0
    b = time.time()
    print(trust_checker(steamid))
    print(time.time()-b)