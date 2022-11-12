import requests
import bs4
import re
from statistics import quantiles
from .bracket2elo import exceptions

def eloScrape(players,surface):
    # scrape elos from the tennisabstract website
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    page = requests.get("http://tennisabstract.com/reports/atp_elo_ratings.html",headers=headers)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    table = soup.find("table", id="reportable")
    Rank = []
    Player = []
    Age = []
    Elo = []
    EloHard = []
    EloClay = []
    EloGrass = []
    for i,row in enumerate(table.find_all('tr')):
        if i==0:
            continue
        # if i==5:
        #     break
        col = row.find_all('td')
        Rank.append(int(col[0].text))
        Player.append(col[1].text.replace("\xa0"," "))
        Age.append(float(col[2].text))
        Elo.append(float(col[3].text))
        EloHard.append(float(col[9].text))
        EloClay.append(float(col[10].text))
        EloGrass.append(float(col[11].text))


    if surface=="clay":
        EloSurface = EloClay
    elif surface=="hard":
        EloSurface = EloHard
    elif surface=="grass":
        EloSurface = EloGrass
    elif surface=="all":
        EloSurface = Elo
    else:
        raise ValueError("surface needs to be one of 'clay', 'hard', 'grass' or 'all' but surface=" + str(surface) + " is not supported.")

    elos = [1650]*len(players)
    elos_found = []
    conflicts = []
    conflicts_indices = []
    for i,p_draw in enumerate(players):
        if p_draw == "Bye":
            elos[i] = 0
            continue
        elif p_draw.startswith("Qualifier"):
            elos[i] = 1
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
            for j,p_elo in enumerate(Player):
                x = re.search(p_draw.split()[1],p_elo) # the index should match the last name
                if x:
                    matches += 1
                    Player_indices.append(j)
        if matches == 1:
            elos[i] = EloSurface[Player_indices[0]]
            elos_found.append(EloSurface[Player_indices[0]])
        elif matches == 0:
            conflicts.append(p_draw)
            conflicts_indices.append(i)
            print("Could not find elo for",p_draw)
        elif matches > 1:
            conflicts.append(p_draw)
            conflicts_indices.append(i)
            print("Found more than one match for",p_draw)
    
    # input for elos that were not found
    quartiles = quantiles(elos_found,n=4)
    # input elos for qualifiers at the first quartile
    for i in range(len(elos)):
        if elos[i] == 1:
            elos[i] = quartiles[0]

    return elos