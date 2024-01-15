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
    draws = soup.find_all(class_="draw")

    # Get only the players and the seed
    rows = draws[0].find_all(class_="stats-item")
    player_names = []
    player_seed = []
    for i,row in enumerate(rows):
        player_info = row.find(class_="name")
        player_names.append(player_info.contents[0].text.strip())
        player_seed.append(player_info.contents[2].text.strip())

    # Get the rankings
    page = requests.get("https://www.atptour.com/en/rankings/singles?rankRange=1-500",headers=headers)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    table = soup.find(class_="mega-table desktop-table").find("tbody")
    rank_rows = table.find_all("tr",recursive=False)
    rank = {}
    for row in rank_rows:
        cols = row.find_all("td",limit=2)
        try:
            # only saving the last name may lead to duplicates (players with the same last name)
            # that silently overwrite each other
            rank[cols[1].find(class_="name").text.split()[-1]] = int(cols[0].text.strip())
        except:
            continue

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
            player_ranking.append(rank[player_names[i].split()[-1]])
        except:
            print("Did not find ranking for player " + player_names[i])
            player_ranking.append(1000)

    results = []
    scores = []
    for draw in draws:
        rows = draw.find_all(class_="draw-item")
        for row in rows:
            player_infos = row.find_all(class_="stats-item")
            if player_infos[0].find(class_="winner") is not None:
                player_name = player_infos[0].find(class_="name").contents[0].text.strip()
                results.append(player_entries[player_names.index(player_name)])
                winner = player_infos[0]
                loser = player_infos[1]
            elif player_infos[1].find(class_="winner") is not None:
                player_name = player_infos[1].find(class_="name").contents[0].text.strip()
                results.append(player_entries[player_names.index(player_name)])
                winner = player_infos[1]
                loser = player_infos[0]
            else:
                results.append("")
                scores.append("")
                continue
            try:
                first_score = winner.find(class_="score-item").text.strip()
                if first_score == "" or first_score == "-":
                    raise
            except:
                scores.append("")
                continue
            winner_score = winner.find_all(class_="score-item")
            loser_score = loser.find_all(class_="score-item")
            score = ""
            for j in range(len(winner_score)):
                winner_spans = winner_score[j].find_all("span")
                loser_spans = loser_score[j].find_all("span")
                score += winner_spans[0].text
                score += loser_spans[0].text
                if winner_spans[1].text != "":
                    score += "(" + winner_spans[1].text + ")"
                elif loser_spans[1].text != "":
                    score += "(" + loser_spans[1].text + ")"
                score += " "
            scores.append(score.strip())

    return {"players":player_entries,"ranking":player_ranking,"results":results,"scores":scores}
