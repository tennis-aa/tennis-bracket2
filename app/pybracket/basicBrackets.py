from random import random
import math

def generateMonkeys(players,n):
    # helper variables
    bracketSize = len(players)
    rounds = math.log(bracketSize,2)
    if not rounds.is_integer():
        raise ValueError("bracketSize has to be 2^n")
    rounds = int(rounds)
    
    counter = [0]*(rounds+1)
    for j in range(rounds):
        counter[j+1] = counter[j] + int(bracketSize/(2**j))

    # generate random brackets
    monkeys = {}
    for k in range(n):
        bracket = []
        for i in range(int(bracketSize/2)):
            if players[2*i]=="Bye":
                bracket.append(2*i+1)
            elif players[2*i+1]=="Bye":
                bracket.append(2*i)
            elif random() < 0.5:
                bracket.append(2*i)
            else:
                bracket.append(2*i+1)
        
        for j in range(1,rounds):
            for i in range(int(bracketSize/(2**(j+1)))):
                if random()<0.5:
                    bracket.append(bracket[counter[j]-bracketSize+2*i])
                else:
                    bracket.append(bracket[counter[j]-bracketSize+2*i+1])
        monkeys["monkey"+str(k)] = bracket

    return monkeys


def generateBots(players,elo,n,sets=3):
    # helper variables
    bracketSize = len(players)
    rounds = math.log(bracketSize,2)
    if not rounds.is_integer():
        raise ValueError("bracketSize has to be 2^n")
    rounds = int(rounds)
    
    counter = [0]*(rounds+1)
    for j in range(rounds):
        counter[j+1] = counter[j] + int(bracketSize/(2**j))

    # generate brackets based on probabilities from elo
    bots = {}
    for k in range(n):
        bracket = []
        bracket_elo = []
        for i in range(int(bracketSize/2)):
            if players[2*i]=="Bye":
                bracket.append(2*i+1)
                bracket_elo.append(elo[2*i+1])
                continue
            elif players[2*i+1]=="Bye":
                bracket.append(2*i)
                bracket_elo.append(elo[2*i])
                continue
            
            Q1 = 10**(elo[2*i]/400)
            Q2 = 10**(elo[2*i+1]/400)
            probability = Q1/(Q1+Q2)
            if sets == 5:
                probability = fiveodds(probability)
            if random() < probability:
                bracket.append(2*i)
                bracket_elo.append(elo[2*i])
            else:
                bracket.append(2*i+1)
                bracket_elo.append(elo[2*i+1])
        
        for j in range(1,rounds):
            for i in range(int(bracketSize/(2**(j+1)))):
                Q1 = 10**(bracket_elo[counter[j]-bracketSize+2*i]/400)
                Q2 = 10**(bracket_elo[counter[j]-bracketSize+2*i+1]/400)
                probability = Q1/(Q1+Q2)
                if sets == 5:
                    probability = fiveodds(probability)
                if random() < probability:
                    bracket.append(bracket[counter[j]-bracketSize+2*i])
                    bracket_elo.append(bracket_elo[counter[j]-bracketSize+2*i])
                else:
                    bracket.append(bracket[counter[j]-bracketSize+2*i+1])
                    bracket_elo.append(bracket_elo[counter[j]-bracketSize+2*i+1])
        bots["bot"+str(k)] = bracket

    return bots

def generateElo(players,elo):
    # helper variables
    bracketSize = len(players)
    rounds = math.log(bracketSize,2)
    if not rounds.is_integer():
        raise ValueError("bracketSize has to be 2^n")
    rounds = int(rounds)
    
    counter = [0]*(rounds+1)
    for j in range(rounds):
        counter[j+1] = counter[j] + int(bracketSize/(2**j))

    # generate brackets based on probabilities from elo
    bracket = []
    bracket_elo = []
    for i in range(int(bracketSize/2)):
        if players[2*i]=="Bye":
            bracket.append(2*i+1)
            bracket_elo.append(elo[2*i+1])
            continue
        elif players[2*i+1]=="Bye":
            bracket.append(2*i)
            bracket_elo.append(elo[2*i])
            continue
        
        if elo[2*i]>elo[2*i+1]:
            bracket.append(2*i)
            bracket_elo.append(elo[2*i])
        else:
            bracket.append(2*i+1)
            bracket_elo.append(elo[2*i+1])
    
    for j in range(1,rounds):
        for i in range(int(bracketSize/(2**(j+1)))):
            if bracket_elo[counter[j]-bracketSize+2*i]>bracket_elo[counter[j]-bracketSize+2*i+1]:
                bracket.append(bracket[counter[j]-bracketSize+2*i])
                bracket_elo.append(bracket_elo[counter[j]-bracketSize+2*i])
            else:
                bracket.append(bracket[counter[j]-bracketSize+2*i+1])
                bracket_elo.append(bracket_elo[counter[j]-bracketSize+2*i+1])
    Elo = {"Elo":bracket}

    return Elo

# The following function computes the probability of winning a 5 set match given the probability of winning a 3 set match.
# The elo ratings used in this package are for 3 set matches. A conversion is necessary for 5 set matches.
# This function was taken from https://github.com/JeffSackmann/tennis_misc/blob/master/fiveSetProb.py
import numpy
 
def fiveodds(p3):
    p1 = numpy.roots([-2, 3, 0, -1*p3])[1]
    p5 = (p1**3)*(4 - 3*p1 + (6*(1-p1)*(1-p1)))
    return p5