from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from datetime import datetime,timezone,timedelta
from . import pybracket
from . import dbfirestore
from . import auth
import json

bp = Blueprint('update', __name__,url_prefix='/update')

@bp.route('/')
@auth.login_required
def index():
    if g.user["user_id"] > 4:
        return redirect(url_for('index'))
    tournament_docs = dbfirestore.db.collection("tournaments").stream()
    tournaments = [i.to_dict() for i in tournament_docs if i.id != "tournamentcount"]
    tournaments.sort(key = lambda x: x["start_time"],reverse=True)
    year_tournament_dict = {}
    for i in tournaments:
        if i["year"] in year_tournament_dict:
            year_tournament_dict[i["year"]].append(i["name"])
        else:
            year_tournament_dict[i["year"]] = [i["name"]]
    return render_template('update/index.jinja',year_tournament_dict=year_tournament_dict)

@bp.route('/<year>/<tournament>',methods=('GET','POST'))
@auth.login_required
def tournament(year,tournament):
    if g.user["user_id"] > 4:
        return redirect(url_for('index'))
    tourn = dbfirestore.get_tournament(tournament,year)
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('index'))

    brack = dbfirestore.db.collection("brackets").where("tournament_id","==",tourn["tournament_id"]).stream()

    b = db2bracket(tourn, brack)

    start_time = datetime.strftime(b.start_time,'%Y-%m-%dT%H:%M')
    end_time = datetime.strftime(b.end_time,'%Y-%m-%dT%H:%M')
    tzlocal = timezone(datetime.utcoffset(b.start_time))
    tz = int(datetime.utcoffset(b.start_time).total_seconds()/3600)

    if request.method == 'POST':
        b.surface = request.form['surface']
        b.sets = int(request.form['sets'])
        b.atplink = request.form['atplink']
        b.start_time = datetime.strptime(request.form['starttime'],'%Y-%m-%dT%H:%M').replace(tzinfo=tzlocal)
        b.end_time = datetime.strptime(request.form['endtime'],'%Y-%m-%dT%H:%M').replace(tzinfo=tzlocal)
        b.points_per_round = [int(request.form['points_per_round'+str(i)]) for i in range(b.rounds)]
        b.elo = [float(request.form['elo'+str(i)]) for i in range(len(b.players))]

        try:
            updated_players = b.updatePlayers()
        except:
            flash("Error actualizando jugadores")
            return redirect(url_for('update.tournament',year=year,tournament=tournament))

        # try:
        if updated_players:
            b.updateElo()
        b.brackets[5] = b.Elobracket()
        elobrack = dbfirestore.db.collection("brackets").where("tournament_id","==",tourn["tournament_id"]).where("user_id","==",5).get()
        if len(elobrack) == 1:
            dbfirestore.update_bracket(elobrack[0].to_dict()["bracket_id"],{"bracket" : b.brackets[5]})
        else:
            dbfirestore.add_bracket(5,tourn["tournament_id"],b.brackets[5])
        b.updateResults(scrape=True)
        bracket2tourn(b,tourn)
        dbfirestore.update_tournament(tourn)
        flash('Cuadro actualizado exitosamente.')
        # except:
        #     flash('Error actualizando el cuadro.')
        return redirect(url_for('update.tournament',year=year,tournament=tournament))

    return render_template('update/tournament.jinja', b=b, start_time = start_time, end_time = end_time, tz = tz)

@bp.route('/newtournament',methods=('GET','POST'))
@auth.login_required
def newtournament():
    if g.user["user_id"] > 4:
        return redirect(url_for('index'))

    if request.method == "POST":
        # try:
        atpinfo = pybracket.ATPdrawScrape(request.form['atplink'])
        elos = pybracket.eloScrape(atpinfo['players'], request.form['surface'])
        start_time = datetime.strptime(request.form['starttime'],'%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['endtime'],'%Y-%m-%dT%H:%M')
        tz = timezone(timedelta(hours=int(request.form["timezone"])))
        start_time = start_time.replace(tzinfo=tz)
        end_time = end_time.replace(tzinfo=tz)
        bracketsize = len(atpinfo['players'])
        results_dict = {'results':[-1]*bracketsize,'scores':[""]*bracketsize,'losers':[],'table_results':{"user": [],"points":[],"potential":[],"position":[],"rank":[],"monkey_rank":[],"bot_rank":[],"prob_winning":[]}}
        dbfirestore.add_tournament(request.form['name'],int(request.form['year']),start_time,end_time,[1,2,3,5,7,10,15],
            request.form['atplink'],bracketsize,request.form['surface'],int(request.form['sets']),
            atpinfo['players'],elos,results_dict)
        return redirect(url_for('update.tournament',year = request.form['year'],tournament=request.form['name']))
        # except:
        #     flash("No se pudo crear el cuadro.")
        #     return render_template("update/newtournament.jinja")

    return render_template("update/newtournament.jinja")


def db2bracket(tourn,brack):
    brackets = {}
    for i in brack:
        bracket = i.to_dict()
        brackets.update({bracket["user_id"] : bracket["bracket"]})
    b = pybracket.Bracket(players=tourn["players"],
                          elo=tourn["elos"],
                          sets=tourn["sets"],
                          results=tourn["results"]['results'],
                          scores=tourn["results"]['scores'],
                          losers=tourn["results"]['losers'],
                          table_results=tourn["results"]['table_results'],
                          brackets=brackets,
                          tournament=tourn["name"],
                          year=tourn["year"],
                          path='',
                          points_per_round=tourn["points_per_round"],
                          atplink=tourn["atplink"],
                          surface=tourn["surface"],
                          start_time=tourn["start_time"],
                          end_time=tourn["end_time"])
    return b

def bracket2tourn(b,tourn):
    tourn["start_time"] = b.start_time
    tourn["end_time"] = b.end_time
    tourn["points_per_round"] = b.points_per_round
    tourn["atplink"] = b.atplink
    tourn["bracketsize"] = b.bracketSize
    tourn["surface"] = b.surface
    tourn["sets"] = b.sets
    tourn["players"] = b.players
    tourn["elos"] = b.elo
    tourn["results"] = {"results":b.results,"scores":b.scores,"losers":b.losers,"table_results":b.table_results}
    return