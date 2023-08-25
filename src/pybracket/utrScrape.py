import requests
import json
import re
from statistics import quantiles
from .bracket2utr import exceptions

def utrScrape(players):
    # There is an api so we do not need to scrape
    utr_data = requests.get("https://api.universaltennis.com/pts/player/top?gender=m&top=500&skip=0")
    if utr_data.status_code != 200:
        print("error fetching utr scores",utr_data.text)
        return [0]*len(players)
    utr_data = json.loads(utr_data.text)
    Player = []
    UTR = []
    for player in utr_data:
        Player.append(player["displayName"])
        UTR.append(player["singlesUtr"])
    utrs = [14.0]*len(players)
    utrs_found = []
    conflicts = []
    conflicts_indices = []
    for i,p_draw in enumerate(players):
        if p_draw == "Bye":
            utrs[i] = 0
            continue
        elif p_draw.startswith("Qualifier"):
            utrs[i] = 1
            continue
        matches = 0
        Player_indices = []
        if p_draw[-1]==")": # if the player entry has a seed, remove the seed from the name
            p_draw_name = " ".join(p_draw.split()[0:-1])
        else:
            p_draw_name = p_draw
        try:
            ind = Player.index(exceptions[p_draw_name])
            matches += 1
            Player_indices.append(ind)
        except:
            for j,p_utr in enumerate(Player):
                x = re.search(p_draw.split()[1],p_utr) # the index should match the last name
                if x:
                    matches += 1
                    Player_indices.append(j)
        if matches == 1:
            utrs[i] = UTR[Player_indices[0]]
            utrs_found.append(UTR[Player_indices[0]])
        elif matches == 0:
            conflicts.append(p_draw)
            conflicts_indices.append(i)
            print("Could not find utr for",p_draw)
        elif matches > 1:
            conflicts.append(p_draw)
            conflicts_indices.append(i)
            print("Found more than one match for",p_draw)
    # input for utrs that were not found
    quartiles = quantiles(utrs_found,n=4)
    # input utrs for qualifiers at the first quartile
    for i in range(len(utrs)):
        if utrs[i] == 1:
            utrs[i] = quartiles[0]
    return utrs