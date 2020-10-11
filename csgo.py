import requests
import re
import json
import matplotlib.pyplot as plt
import numpy as np
import argparse


API_KEY = ""

parser = argparse.ArgumentParser(description='CSGO weapon stats')
parser.add_argument('apikey',
                    type=str,
                    help='A required API key argument.')
parser.add_argument('profilename',
                    type=str,
                    help='A required profilename string argument steamcommunity.com/id/<<this_value>>/.')
parser.add_argument('-W','--weapons',
                    type=str,
                    help="Specify up to 5 weapons delimited with comma for comparison.  Default are: ak47, awp, negev, ssg08, m4a1.")
args = parser.parse_args()

EXIT = False

if not args.apikey:
    print("Bad api key")
    EXIT = True

if not args.profilename:
    print("Bad profilename")
    EXIT = True

weapons = []
if args.weapons:
    weapons_list = set({
        'deagle', 'glock', 'elite', 'fiveseven', 'awp', 'ak47',
        'aug', 'famas', 'g3sg1', 'p90', 'mac10', 'ump45',
        'xm1014', 'm249', 'hkp2000', 'p250', 'sg556', 'scar20',
        'ssg08', 'mp7', 'mp9', 'nova', 'negev', 'sawedoff',
        'bizon', 'tec9', 'mag7', 'm4a1', 'galilar', 'taser',
    })
    weapons = set(re.findall(r'(?:^|(?<=,))[^,]*', args.weapons))

    if len(weapons) < 2:
        print("Specify at least two different weapons.")
        EXIT = True
    if not weapons.issubset(weapons_list):
        print("Check weapons names.")
        EXIT = True

if EXIT:
    exit()

API_KEY = args.apikey

class SteamProfile:
    def __init__(self, steamURL, profileID=""):
        self.steamURL = "https://steamcommunity.com/id/" + steamURL + "/"
        self.profileID = profileID

    steamID = ""
    steamURL = ""
    profileID = ""
    csgoStats = {}
    cleanCsgoStats = {}
    weaponsStats = {}

    def __getProfileID(self):
        try:
            self.profileID = re.search(r'/id/(.*?)/', self.steamURL).group(1)
        except AttributeError:
            self.profileID = None

    def __cleanCsgoStats(self):
        json_str = str(self.csgoStats)
        json_str = re.search(
            r'\{(.*?)\[(.*?)\](.*?)\]\}', json_str.replace(' ', '')).group(2).replace("'", '"')
        properties = re.findall(r'\{"name":"(.*?)","value":(.*?)\}', json_str)

        for p in properties:
            self.cleanCsgoStats[p[0]] = p[1]
        self.__getWeaponStats()

    def __getWeaponStats(self):
        weapons_shots = re.findall(
            r"total_shots_(.*?)\'", str(self.cleanCsgoStats))
        _weapons_hits = re.findall(
            r"total_hits_(.*?)\'", str(self.cleanCsgoStats))

        for weapon in weapons_shots:
            if weapon != 'hit' and weapon != 'fired':
                self.weaponsStats[weapon] = []
                self.weaponsStats[weapon].append(
                    int(self.cleanCsgoStats['total_shots_'+weapon]))
                try:
                    self.weaponsStats[weapon].append(
                        int(self.cleanCsgoStats['total_hits_'+weapon]))
                except KeyError:
                    self.weaponsStats[weapon].append(0)

    def getSteamID(self):
        self.__getProfileID()
        if self.profileID:
            request = requests.get(
                'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='+API_KEY+'&vanityurl='+self.profileID)
            self.steamID = request.json()['response']['steamid']
            print(f'SteamID: {self.steamID}')

    def getCsgoStats(self):
        if self.profileID:
            request = requests.get(
                'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key='+API_KEY+'&steamid='+self.steamID)
            print(f'API link: {request.url}')
            try:
                self.csgoStats = request.json()
                with open('csgo_stats.json', 'w') as stats_file:
                    json.dump(self.csgoStats, stats_file)
                self.__cleanCsgoStats()
            except json.decoder.JSONDecodeError:
                print("Wrong profile settings. Check if your steam account is properly configured.")
                exit()

    def pieChart(self, weapons):
        """'deagle', 'glock', 'elite', 'fiveseven', 'awp', 'ak47'"""
        """'aug', 'famas', 'g3sg1', 'p90', 'mac10', 'ump45',"""
        """'xm1014', 'm249', 'hkp2000', 'p250', 'sg556', 'scar20'"""
        """'ssg08', 'mp7', 'mp9', 'nova', 'negev', 'sawedoff'"""
        """'bizon', 'tec9', 'mag7', 'm4a1', 'galilar', 'taser'"""
        _, ax = plt.subplots()

        size = 0.3

        cmap = plt.get_cmap("tab20c")
        outer_colors = cmap(np.arange(5)*4)
        inner_colors = cmap(np.array([1, 2, 5, 6, 9, 10, 13, 14, 17, 18]))

        try:
            weapons = {el:self.weaponsStats[el] for el in weapons}
        except KeyError as e:
            print(f"Wrong weapon name {e}. Steam API changed?")
            exit()

        v2 = np.array(list(weapons.values()))
        v1 = np.array(list(weapons.values()))

        wedges, _ = ax.pie(v1[:, 0], radius=1, colors=outer_colors,
                               wedgeprops=dict(width=size, edgecolor='w'))

        for i in range(len(v2)):
            v2[i] = [v2[i][0]-v2[i][1], v2[i][1]]

        ax.pie(v2.flatten(), radius=1-size, colors=inner_colors,
               wedgeprops=dict(width=size, edgecolor='w'))
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)

        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")
        v2 = np.array(list(weapons.values()))
        v1 = np.array(list(weapons.values()))
        recipe = []
        for i, weapon in enumerate(weapons.keys()):
            recipe.append(weapon+" ("+str(v2.flatten()[2*i+1])+"/"+str(v2.flatten()[2*i])+")="+str(
                round(100*float(v2.flatten()[2*i+1])/float(v2.flatten()[2*i]), 1))+"%")
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment, **kw)
        ax.set(aspect="equal", title='shots hit/shots fired')
        plt.show()

    def __str__(self):
        json_str = str(self.csgoStats)
        json_str = re.search(
            r'\{(.*?)\[(.*?)\](.*?)\]\}', json_str.replace(' ', '')).group(2).replace("'", '"')
        properties = re.findall(r'\{"name":"(.*?)","value":(.*?)\}', json_str)
        data = {}
        for p in properties:
            data[p[0]] = p[1]

        line = "Total kills: {}\nTotal deaths: {}\nIngame time: {}h{}m\nOverall KD ratio: {}"
        return line.format(data['total_kills'],
                           data['total_deaths'],
                           str(int(data['total_time_played'])//3600),
                           str(int(data['total_time_played'])//60 % 60),
                           float(data['total_kills'])/float(data['total_deaths']))


profile = SteamProfile(
    args.profilename)

profile.getSteamID()
profile.getCsgoStats()
profile.pieChart(weapons or ['awp', 'ak47', 'm4a1', 'ssg08', 'negev'])
