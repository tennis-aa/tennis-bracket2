from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from . import pybracket
from . import models
from . import auth

bp = Blueprint('update', __name__,url_prefix='/update')

@bp.route('/')
def index():
    tourn = models.Tournament.query.all()
    tourn.sort(key = lambda x: x.start_time)
    year_tournament_dict = {}
    for i in tourn:
        if i.year in year_tournament_dict:
            year_tournament_dict[i.year].append(i.name)
        else:
            year_tournament_dict[i.year] = [i.name]
    return render_template('update/index.jinja',year_tournament_dict=year_tournament_dict)

@bp.route('/<year>/<tournament>',methods=('GET','POST'))
def tournament(year,tournament):
    tourn = models.Tournament.query.filter((models.Tournament.name == tournament) & (models.Tournament.year == year)).first()
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('update.index'))
    
    brack = models.BracketModel.query.filter(models.BracketModel.tournament_id == tourn.tournament_id).all()
    
    b = db2bracket(tourn, brack)

    if request.method == 'POST':
        return "work in progress"

    return render_template('update/tournament.jinja', b=b)

@bp.route('/newtournament',methods=('GET','POST'))
def newtournament():
    if request.method == "POST":
        atpinfo = pybracket.ATPdrawScrape(request.form['atplink'])
        elos = pybracket.eloScrape(atpinfo['players'], request.form['surface'])
        b = pybracket.Bracket(players=atpinfo['players'],elo=elos,sets=request.form['sets'],results=atpinfo['results'],
            scores=atpinfo['scores'],tournament=request.form['name'],year=request.form['year'],
            atplink=request.form['atplink'],surface=request.form['surface'],start_time=request.form['starttime'],
            end_time=request.form['endtime'])
        print(b)
        print(type(b.start_time))

        return "Work in progress" # should return the update page to input elo ratings for nonmatches
    
    return render_template("update/newtournament.jinja")


def db2bracket(tourn,brack):
    brackets = {}
    for i in brack:
        brackets.update({i.user_id:i.bracket})
    b = pybracket.Bracket(players = tourn.players,
                          elo=tourn.elos,
                          sets=tourn.sets,
                          results=tourn.results['results'],
                          scores=tourn.results['scores'],
                          losers=tourn.results['losers'],
                          table_results=tourn.results['table_results'],
                          brackets=brackets,
                          tournament=tourn.name,
                          year=tourn.year,
                          path='',
                          points_per_round=tourn.points_per_round,
                          atplink=tourn.atplink,
                          surface=tourn.surface)
    return b