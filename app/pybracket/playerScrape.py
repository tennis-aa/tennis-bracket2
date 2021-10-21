import bs4
import os
import json
import re
import math
from selenium import webdriver # requires the installion of geckodriver and its addition to the path

# scrape players from ATP website
# This is working great! player_names has all the players by round, so it includes results
# It does not include the seed and has the long names

def ATPdrawScrape(atplink):
    fireFoxOptions = webdriver.firefox.options.Options()
    fireFoxOptions.headless = True
    browser = webdriver.Firefox(options=fireFoxOptions)
    browser.get(atplink)
    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    browser.quit()
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
    
    # player_entries are the combination of player names and seeds, with names only displaying the first letter of the first name
    player_entries = []
    qualifier_count = 0
    for i in range(len(player_names)):
        if player_names[i] == "Bye":
            player_entries.append("Bye")
            continue
        if player_names[i] == "Qualifier":
            qualifier_count += 1
            player_entries.append("Qualifier{}".format(qualifier_count))
            continue
        player_name_list = player_names[i].split()
        if re.search("Daniel Elahi",player_names[i]):
            player_entry = " ".join(["DE"] + player_name_list[2:] + [player_seed[i]]).strip()
        elif re.search("Juan Ignacio",player_names[i]):
            player_entry = " ".join(["JI"] + player_name_list[2:] + [player_seed[i]]).strip()
        elif re.search("Marcelo Tomas",player_names[i]):
            player_entry = " ".join(["MT"] + player_name_list[2:] + [player_seed[i]]).strip()
        elif re.search("Holger Vitus Nodskov",player_names[i]):
            player_entry = " ".join(["HVN"] + player_name_list[3:] + [player_seed[i]]).strip()
        else:
            player_entry = " ".join([player_name_list[0][0]] + player_name_list[1:] + [player_seed[i]]).strip()
        player_entries.append(player_entry)

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

    return {"players":player_entries,"results":results,"scores":scores}

if __name__ == "__main__":
    x = ATPdrawScrape("https://www.atptour.com/en/scores/current/roland-garros/520/draws")


