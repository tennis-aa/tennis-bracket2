import os
import bs4
import math
import requests
from .ATP2bracket import exceptions

# scrape players from ATP website
def ATPdrawScrape(atplink):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    page = requests.get(atplink,headers=headers)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    draw = soup.find(id="scoresDrawTable").find("tbody")
    rows = draw.findChildren("tr",recursive=False)

    # Get only the players and the seed
    player_names = []
    player_seed = []
    for i,row in enumerate(rows):
        match = row.find("td")
        for j,player in enumerate(match.find_all("tr")):
            player_info = player.find_all("td")
            player_names.append(player_info[2].text.strip())
            player_seed.append(player_info[1].text.strip())

    # Get the rankings
    page = requests.get("https://www.atptour.com/en/rankings/singles?rankRange=1-500",headers=headers)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    table = soup.find(id="player-rank-detail-ajax").find("tbody")
    rank_rows = table.findChildren("tr",recursive=False)
    rank = {}
    for row in rank_rows:
        rank[row.find(class_="player-cell").text.strip()] = int(row.find(class_="rank-cell").text.strip())
    
    # player_entries are the combination of player names and seeds, with names only displaying the first letter of the first name
    # Players with more than one first name are displayed with the first letter of each first name by looking for those exceptions in ATP2bracket.py
    player_entries = []
    player_ranking = []
    qualifier_count = 0
    for i in range(len(player_names)):
        if player_names[i] == "Bye":
            player_entries.append("Bye")
            player_ranking.append(10000)
            continue
        if player_names[i].lower().startswith("qualifier"):
            qualifier_count += 1
            player_entries.append("Qualifier{}".format(qualifier_count))
            player_ranking.append(500)
            continue

        try:
            player_entry = (exceptions[player_names[i]] + " " + player_seed[i]).strip()
        except:
            player_name_list = player_names[i].split()
            player_entry = " ".join([player_name_list[0][0]] + player_name_list[1:] + [player_seed[i]]).strip()
        player_entries.append(player_entry)

        # ranking
        try:
            player_ranking.append(rank[player_names[i]])
        except:
            player_ranking.append(1000)

    rounds = int(math.log2(len(player_entries)))
    result_entries = [[] for _ in range(rounds)]
    score_entries = [[] for _ in range(rounds)]
    for i,row in enumerate(rows):
        for rd,col in enumerate(row.findChildren("td",recursive=False)):
            if rd == 0:
                continue
            x = col.find_all(class_="scores-draw-entry-box")
            for box in col.find_all(class_="scores-draw-entry-box"):
                player_links = box.find_all(class_="scores-draw-entry-box-players-item")
                score_links = box.find_all(class_="scores-draw-entry-box-score")
                if len(player_links) == 0:
                    result_entries[rd-1].append("")
                    score_entries[rd-1].append("")
                else:
                    for j in range(len(player_links)):
                        player_name = player_links[j].text
                        player_name = player_name.strip()
                        ind = player_names.index(player_name)
                        result_entries[rd-1].append(player_entries[ind])
                        score_contents = score_links[j].contents
                        score_raw = ""
                        for i in range(len(score_contents)):
                            if score_contents[i].name == "sup":
                                score_raw += "(" + score_contents[i].text + ")"
                            else:
                                score_raw += str(score_contents[i])
                        score_entries[rd-1].append(" ".join(score_raw.split()))

    results = []
    scores = []
    for i in range(len(result_entries)):
        results = results + result_entries[i]
        scores = scores + score_entries[i]

    return {"players":player_entries,"ranking":player_ranking,"results":results,"scores":scores}



