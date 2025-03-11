import os
import math
import json
import copy
from random import random
from . import playerScrape
from . import eloScrape
from . import utrScrape
from . import basicBrackets
from datetime import datetime

class Bracket:
    def __init__(self,players=[],ranking=[],elo=[],utr=[],sets=3,results=[],scores=[],losers=[],table_results={"user": [],"points":[],"potential":[],"position":[],"rank":[],"monkey_rank":[],"bot_rank":[],"prob_winning":[]},
                brackets={},tournament="",year=0,path="",points_per_round=[1,2,3,5,7,10,15],atplink="",surface="all",
                start_time=datetime(2021,1,1,0,0,0,0),end_time=datetime(2021,1,1,0,0,0,0)):
        self.players = players
        self.bracketSize = len(players)
        self.ranking = ranking
        self.elo = elo
        self.utr = utr
        self.sets = sets
        self.results = results
        self.scores = scores
        self.losers = losers
        self.table_results = table_results
        if self.bracketSize == 0:
            self.rounds = 0
        else:
            self.rounds = int(math.log2(self.bracketSize))
        self.brackets = brackets
        self.tournament = tournament
        self.year = year
        self.path = path
        self.points_per_round = points_per_round
        self.atplink = atplink
        self.surface = surface
        self.counter = [0]*(self.rounds+1)
        for j in range(self.rounds):
            self.counter[j+1] = self.counter[j] + int(self.bracketSize/(2**j))
        self.start_time = start_time
        self.end_time = end_time

    def loadFromFolder(self,path=None):
        if path is not None:
            self.path = path

        with open(os.path.join(self.path, "config.json"),"r", encoding="utf-8") as f:
            config = json.load(f)
        self.tournament = config["tournament"]
        self.points_per_round = config["points_per_round"]
        self.atplink = config["atplink"]
        self.bracketSize = config["bracketSize"]
        if self.bracketSize == 0:
            self.rounds = 0
        else:
            self.rounds = int(math.log2(self.bracketSize))
        self.counter = [0]*(self.rounds+1)
        for j in range(self.rounds):
            self.counter[j+1] = self.counter[j] + int(self.bracketSize/(2**j))
        self.surface = config["surface"]
        try:
            self.sets = config["sets"]
        except:
            self.sets = 3
        with open(os.path.join(self.path, "players.json"),"r") as f:
            players_json = json.load(f)
        self.players = players_json["players"]
        self.elo = players_json["elo"]
        self.utr = players_json["utr"] if "utr" in players_json else []
        self.ranking = players_json["ranking"] if "ranking" in players_json else []
        if len(self.players) != self.bracketSize:
            print("Warning: the number of players and the bracketSize do not match.")

        if os.path.exists(os.path.join(self.path, "brackets.json")):
            with open(os.path.join(self.path, "brackets.json"),"r", encoding="utf-8") as f:
                self.brackets = json.load(f)
        else:
            self.brackets = {}
        
        if os.path.exists(os.path.join(self.path, "results.json")):
            with open(os.path.join(self.path, "results.json"),"r", encoding="utf-8") as f:
                results_json = json.load(f)
            self.results = results_json["results"]
            self.scores = results_json["scores"]
            self.losers = results_json["losers"]
            self.table_results = results_json["table_results"]
        else:
            self.results = [-1]*(self.bracketSize - 1)
            self.scores = [""]*(self.bracketSize - 1)
            self.losers = []
            self.table_results = {"user": [],"points":[],"potential":[],"position":[],"rank":[],"monkey_rank":[],"bot_rank":[]}

    def computePoints(self,bracket):
        if len(bracket) != (self.bracketSize - 1):
            raise ValueError("The bracket is not the correct length. The correct length is " + str(self.bracketSize-1))
        points = 0
        rd = 0
        for i in range(len(bracket)):
            if i+self.bracketSize >= self.counter[rd+2]:
                rd = rd+1
            if bracket[i] == self.results[i] and self.results[i] != -1:
                points = points + self.points_per_round[rd]

        # deduct points from byes
        for i in range(len(self.players)):
            if self.players[i] == "Bye":
                points = points-self.points_per_round[0]

        return points

    def computePotential(self,bracket):
        if len(bracket) != self.bracketSize - 1:
            raise ValueError("The bracket is not the correct length> The correct is " + str(self.bracketSize-1))
        potential = 0
        rd = 0
        for i in range(len(bracket)):
            if i+self.bracketSize >= self.counter[rd+2]:
                rd = rd + 1
            if bracket[i] == -1:
                continue
            if self.results[i] == bracket[i]:
                potential = potential + self.points_per_round[rd]
            elif self.results[i]==-1 and not (bracket[i] in self.losers):
                potential = potential + self.points_per_round[rd]
            
        for p in self.players:
            if p == "Bye":
                potential -= self.points_per_round[0]

        return potential

    def computeMaxPotential(self):
        potential = 0
        matches = self.bracketSize/2
        for r in range(self.rounds):
            potential += matches * self.points_per_round[r]
            matches /= 2

        for p in self.players:
            if p == "Bye":
                potential -= self.points_per_round[0]

        return int(potential)

    def updatePlayers(self):
        ATPData = playerScrape.ATPdrawScrape(self.atplink) # players, results, scores
        players = ATPData["players"]
        conflicts_old = []
        conflicts_new = []
        for i in range(len(self.players)):
            if self.players[i] != players[i]:
                conflicts_old.append(self.players[i]) 
                conflicts_new.append(players[i])

        # method to update changes to the draw
        if len(conflicts_old)>0:
            print("The following conflicts were found:")
            print(json.dumps({conflicts_old[i]:conflicts_new[i] for i in range(len(conflicts_old))},indent=4))
            # change = input("Do you want to update the players? [y/n]: ")
            # if change != "y" and change != "yes":
            #     raise Exception("You will not be able to update results if there are conflicts between the bracket files and the ATP website.")

            self.players = players
            self.ranking = ATPData["ranking"]

            print("You can run method Bracket.updateElo() to update the elo ratings.")
            return True
        else:
            print("Players are up-to-date.")
            return False
    
    def updateElo(self,player=None,elo=None):
        if player==None or elo==None:
            elos = eloScrape.eloScrape(self.players,self.surface)
            self.elo = elos
        else:
            self.elo[self.players.index(player)] = elo
        return

    def updateUTR(self,player=None,utr=None):
        if player==None or utr==None:
            utrs = utrScrape.utrScrape(self.players)
            self.utr = utrs
        else:
            self.utr[self.players.index(player)] = utr
        return

    def Elobracket(self):
        return basicBrackets.generateElo(self.elo)

    def UTRbracket(self):
        return basicBrackets.generateElo(self.utr)

    def rankingBracket(self):
        return basicBrackets.generateElo([-i for i in self.ranking])

    def updateBrackets(self,user,bracket):
        self.brackets[user] = bracket
        return

    def updateResults(self,scrape=True):
        if scrape:
            ATPData = playerScrape.ATPdrawScrape(self.atplink) # players, results, scores
            players = ATPData["players"]
            results = ATPData["results"]
            results = playernames2indices(ATPData["results"],players)
            scores = ATPData["scores"]
            print("Data successfully downloaded...")
        else:
            players = self.players
            results = self.results
            scores = self.scores

        for i in range(len(self.players)):
            if self.players[i] != players[i]:
                raise Exception("There is a conflict betwen the players found on the ATP website and the bracket records. Run the Bracket.updatePlayers() method to resolve conflicts.")

        self.results = results
        self.scores = scores

        losers = []
        for i in range(int(self.bracketSize/2)):
            if results[i] != -1:
                if results[i] == 2*i and players[2*i+1] != "Bye":
                    losers.append(2*i+1)
                elif results[i] == 2*i+1 and players[2*i] != "Bye":
                    losers.append(2*i)
        
        for j in range(2,self.rounds+1):
            for i in range(int(self.bracketSize/(2**j))):
                if results[self.counter[j]+i-self.bracketSize] != -1:
                    if results[self.counter[j]+i-self.bracketSize] == results[self.counter[j-1]+2*i-self.bracketSize]:
                        losers.append(results[self.counter[j-1]+2*i+1-self.bracketSize])
                    elif (results[self.counter[j]+i-self.bracketSize] == results[self.counter[j-1]+2*i+1-self.bracketSize]):
                        losers.append(results[self.counter[j-1]+2*i-self.bracketSize])
        self.losers = losers

        # Define the object that contains the standings
        table_results = {"user": [],"points":[],"potential":[],"position":[],
            "rank":[],"monkey_rank":[],"bot_rank":[],"prob_winning":[],"elo_points":0,
            "utr_points":0,"ranking_points":0,"max_points":0,"max_potential":0}
        # compute points and positions for all participants
        entries = []
        for key in self.brackets:
            points = self.computePoints(self.brackets[key])
            entries.append({"user":key,"points":points,"position":1,"rank":""})
        entries.sort(key=lambda x:x["points"],reverse=True)
        nr_users = len(entries)
        for i in range(1,nr_users):
            if entries[i]["points"] == entries[i-1]["points"]:
                entries[i]["position"] = entries[i-1]["position"]
            else:
                entries[i]["position"] = i+1

        # compute rank
        for i in range(nr_users):
            if entries[i]["position"] <= math.ceil(nr_users/2):
                entries[i]["rank"] = "top " + str(round((entries[i]["position"]-1/2)/nr_users*100)) + "%"
            else:
                entries[i]["rank"] = "bot " + str(round((nr_users-entries[i]["position"]+1/2)/nr_users*100)) + "%"
            table_results["user"].append(entries[i]["user"])
            table_results["points"].append(entries[i]["points"])
            table_results["position"].append(entries[i]["position"])
            table_results["rank"].append(entries[i]["rank"])

        # compute potential points
        for i in range(nr_users):
            potential = self.computePotential(self.brackets[table_results["user"][i]])
            table_results["potential"].append(potential)

        # compute rank among monkeys
        monkey_points = self.monkey_points(10000)
        monkey_points.sort(reverse=True)
        for i in range(nr_users):
            if table_results["points"][i] < monkey_points[-1]:
                table_results["monkey_rank"].append(100)
                continue
            for j in range(len(monkey_points)):
                if table_results["points"][i] >= monkey_points[j]:
                    table_results["monkey_rank"].append(round(j/len(monkey_points)*100))
                    break

        # compute rank among bots
        bot_points = self.bot_points(10000)
        bot_points.sort(reverse=True)
        for i in range(nr_users):
            if table_results["points"][i] < bot_points[-1]:
                table_results["bot_rank"].append(100)
                continue
            for j in range(len(bot_points)):
                if table_results["points"][i] >= bot_points[j]:
                    table_results["bot_rank"].append(round(j/len(bot_points)*100))
                    break

        # Compute probability of winning
        reps = 10000
        outcomes = self.sim_results(reps)
        prob_winning = [0.0]*len(table_results["user"])
        for outcome in outcomes:
            self.results = outcome # to compute points, temporarily change the results
            # compute the points obtained for a given simulated outcome
            points = []
            for user in table_results["user"]:
                points.append(self.computePoints(self.brackets[user]))
            maxpoints = max(points, default=0)

            # who would have won?
            winners = []
            for i,p in enumerate(points):
                if p == maxpoints:
                    winners.append(i)
 
            # If there are more than one winner "distribute the pot"
            for i in winners:
                prob_winning[i] += 1/reps/len(winners)

        self.results = results # change results back to the true results
        table_results["prob_winning"] = prob_winning

        # Compute points of elo, utr, and ranking
        if (len(self.elo) != 0):
            table_results["elo_points"] = self.computePoints(self.Elobracket())

        if (len(self.utr) != 0):
            table_results["utr_points"] = self.computePoints(self.UTRbracket())

        if (len(self.ranking) != 0):
            table_results["ranking_points"] = self.computePoints(self.rankingBracket())

        table_results["max_points"] = self.computePoints(self.results)
        table_results["max_potential"] = self.computeMaxPotential()

        self.table_results = table_results
        return

    def monkey_points(self,n):
        monkeys = basicBrackets.generateMonkeys(self.players, n)
        monkey_points = []
        for monkey in monkeys:
            monkey_points.append(self.computePoints(monkey))
        return monkey_points

    def bot_points(self,n):
        c0 = 2
        c1 = 2
        def probability_modifier(probability,bracketSize,round,points_per_round):
            c = 1 + c0 *(1 - ((round-1)/(self.rounds - 1))**c1)
            return 1 - (2*(1-probability))**c/2
        bots = basicBrackets.generateBots(self.elo, n, self.sets, self.points_per_round, probability_modifier)
        bot_points = []
        for bot in bots:
            bot_points.append(self.computePoints(bot))
        return bot_points

    def sim_results(self,n):
        # Get the elos of the players in the results list
        results_elo = []
        for i in self.results:
            if i == -1:
                results_elo.append(0)
            else:
                results_elo.append(self.elo[i])
        
        # generate a dict of possible scenarios according to the elos. Similar to generating bot brackets but now we fix the results that have already happened
        output = []
        for k in range(n):
            bracket = []
            bracket_elo = []
            for i in range(int(self.bracketSize/2)):
                if self.results[i] != -1:
                    bracket.append(self.results[i])
                    bracket_elo.append(results_elo[i])
                    continue
                elif self.players[2*i]=="Bye":
                    bracket.append(2*i+1)
                    bracket_elo.append(self.elo[2*i+1])
                    continue
                elif self.players[2*i+1]=="Bye":
                    bracket.append(2*i)
                    bracket_elo.append(self.elo[2*i])
                    continue

                Q1 = 10**(self.elo[2*i]/400)
                Q2 = 10**(self.elo[2*i+1]/400)
                probability = Q1/(Q1+Q2)
                if self.sets == 5:
                    probability = fiveodds_eff(probability)
                if random() < probability:
                    bracket.append(2*i)
                    bracket_elo.append(self.elo[2*i])
                else:
                    bracket.append(2*i+1)
                    bracket_elo.append(self.elo[2*i+1])

            for j in range(1,self.rounds):
                for i in range(int(self.bracketSize/(2**(j+1)))):
                    if self.results[self.counter[j+1]-self.bracketSize+i] != -1:
                        bracket.append(self.results[self.counter[j+1]-self.bracketSize+i])
                        bracket_elo.append(results_elo[self.counter[j+1]-self.bracketSize+i])
                        continue
                    Q1 = 10**(bracket_elo[self.counter[j]-self.bracketSize+2*i]/400)
                    Q2 = 10**(bracket_elo[self.counter[j]-self.bracketSize+2*i+1]/400)
                    probability = Q1/(Q1+Q2)
                    if self.sets == 5:
                        probability = fiveodds_eff(probability)
                    if random() < probability:
                        bracket.append(bracket[self.counter[j]-self.bracketSize+2*i])
                        bracket_elo.append(bracket_elo[self.counter[j]-self.bracketSize+2*i])
                    else:
                        bracket.append(bracket[self.counter[j]-self.bracketSize+2*i+1])
                        bracket_elo.append(bracket_elo[self.counter[j]-self.bracketSize+2*i+1])
            output.append(bracket)
        return output

    def saveToFolder(self):
        with open(os.path.join(self.path, "config.json"),"w", encoding="utf-8") as f:
            f.write(json.dumps({"tournament":self.tournament,"points_per_round": self.points_per_round,"atplink":self.atplink,"bracketSize":self.bracketSize,"surface":self.surface,"sets":self.sets},indent=4))
        with open(os.path.join(self.path, "players.json"),"w", encoding="utf-8") as f:
            f.write(json.dumps({"players": self.players, "elo": self.elo, "utr":self.utr, "ranking":self.ranking}))
        with open(os.path.join(self.path, "brackets.json"),"w", encoding="utf-8") as f:
            f.write(json.dumps(self.brackets))
        with open(os.path.join(self.path, "results.json"),"w", encoding="utf-8") as f:
            f.write(json.dumps({"results":self.results,"scores":self.scores,"losers":self.losers,"table_results":self.table_results}))

# END OF CLASS


def playerUpdate(player_list,players_old,players_new):

    if len(players_old) != len(players_new):
        raise ValueError("The list of old and new players has to be the same length.")

    # First replace all conflicts with another string to avoid double replacing players that were just moved in the draw
    for i,pl in enumerate(players_old):
        player_list = ["NEWPLAYER"+str(i) if j == pl else j for j in player_list]

    # Now replace with the new player
    for i,pl in enumerate(players_new):
        player_list = [pl if j == "NEWPLAYER"+str(i) else j for j in player_list]

    return player_list


# The following function computes the probability of winning a 5 set match given the probability of winning a 3 set match.
# The elo ratings used in this package are for 3 set matches. A conversion is necessary for 5 set matches.
# This function was taken from https://github.com/JeffSackmann/tennis_misc/blob/master/fiveSetProb.py

# import numpy
 
# def fiveodds(p3):
#     p1 = numpy.roots([-2, 3, 0, -1*p3])[1]
#     p5 = (p1**3)*(4 - 3*p1 + (6*(1-p1)*(1-p1)))
#     return p5

# Because it is too computationally expensive to solve the cubic equation numerically, the following does the same
# computation using the cubic formula
def fiveodds_eff(p3):
    p1 = cubic_formula(-2,3,0,-p3,2).real
    p5 = (p1**3)*(4 - 3*p1 + (6*(1-p1)*(1-p1)))
    return p5

def cubic_formula(a,b,c,d,k):
    # https://en.wikipedia.org/wiki/Cubic_equation#General_cubic_formula
    delta0 = b**2 - 3*a*c
    delta1 = 2*b**3 - 9*a*b*c +27*a**2*d
    xi = (-1+(-3)**(1/2))/2
    C = xi**k*((delta1+(delta1**2-4*delta0**3)**(1/2))/2)**(1/3)
    x = -1/(3*a)*(b+C+delta0/C)
    return x

def playernames2indices(target_list,player_list):
    x = []
    for i in target_list:
        for j,player in enumerate(player_list):
            if i == player:
                x.append(j)
                break
            if (j==len(player_list)-1):
                x.append(-1)
    return x