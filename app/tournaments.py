from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import models
from . import auth

bp = Blueprint('tournaments', __name__)

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
    return render_template('index.jinja',year_tournament_dict=year_tournament_dict)

@bp.route('/<year>/<tournament>')
@auth.login_required
def bracket(year,tournament):
    
    tourn = models.Tournament.query.filter((models.Tournament.name == tournament) & (models.Tournament.year == year)).first()
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('index'))

    brack = models.BracketModel.query.filter(models.BracketModel.tournament_id == tourn.tournament_id).all()
    users = models.User.query.filter(models.User.user_id.in_(tourn.results['table_results']['user'])).all()
    users = {i.user_id:i.username for i in users}
    brackets = {}
    for i in brack:
        user = users[i.user_id]
        brackets.update({user:[tourn.players[j] for j in i.bracket]})

    results_dict = tourn.results
    results_dict['results'] = [tourn.players[j] if j>=0 else "" for j in results_dict['results']]
    results_dict['losers'] = [tourn.players[j] for j in results_dict['losers']]
    results_dict['table_results']['user'] = [users[i] for i in results_dict['table_results']['user']]
    
    render_vars = {'bracketSize':tourn.bracketsize,'players':tourn.players,'brackets':brackets,
        'results_dict':results_dict}
    return bracketRender('bracket',year,tournament,render_vars)

@bp.route('/<year>/<tournament>/submit',methods=('GET','POST'))
@auth.login_required
def submit(year,tournament):
    tourn = models.Tournament.query.filter((models.Tournament.name == tournament) & (models.Tournament.year == year)).first()
    brack = models.BracketModel.query.filter((models.BracketModel.tournament_id == tourn.tournament_id) & (models.BracketModel.user_id == g.user.user_id)).first()
    if brack:
        bracket = brack.bracket
    else:
        bracket = [-1]*(tourn.bracketsize-1)

    if request.method == 'GET':
        render_vars = {'bracketSize':tourn.bracketsize,'players':tourn.players,
            'elos':tourn.elos,'bracket':[tourn.players[j] if j>=0 else '' for j in bracket]}

        return bracketRender('submit',year,tournament,render_vars)
    elif request.method == 'POST':
        for i in range(tourn.bracketsize-1):
            try:
                bracket[i] = tourn.players.index(request.form['select{}'.format(tourn.bracketsize+i)])
            except:
                pass
        if brack:
            models.BracketModel.query.filter((models.BracketModel.tournament_id == tourn.tournament_id) & (models.BracketModel.user_id == g.user.user_id)).update({'bracket':bracket})
            models.db.session.commit()
        else:
            brack = models.BracketModel(g.user.user_id,tourn.tournament_id,bracket)
            models.db.session.add(brack)
            models.db.session.commit()
        return redirect(url_for("tournaments.submit",year=year,tournament=tournament))
    else:
        return redirect(url_for('index'))

@bp.route('/<year>/<tournament>/table')
@auth.login_required
def table(year,tournament):

    tourn = models.Tournament.query.filter((models.Tournament.name == tournament) & (models.Tournament.year == year)).first()

    users = models.User.query.filter(models.User.user_id.in_(tourn.results['table_results']['user'])).all()
    users = {i.user_id:i.username for i in users}

    tourn.results['table_results']['user'] = [users[i] for i in tourn.results['table_results']['user']]
    print(tourn.results['table_results'])
    render_vars = {'bracketSize':tourn.bracketsize,'table_results':tourn.results['table_results']}
    return bracketRender('table',year,tournament,render_vars)



import math
def bracketRender(render_type,year,tournament,render_vars,cellheight=16,vspace=32,hspace=100,linewidth=1):

    bracketSize = render_vars['bracketSize']
    rounds = math.log(bracketSize,2)
    if not rounds.is_integer():
            raise ValueError("bracketSize has to be 2^n")
    rounds = int(rounds)

    # input variables
    counter = [0]*(rounds+1)
    for j in range(rounds):
        counter[j+1] = counter[j] + int(bracketSize/(2**j))
    # print(counter)

    render_vars.update({"rounds" : rounds, "counter" : counter, "year" : year, "tournament": tournament,
    "cellheight": cellheight, "vspace": vspace, "hspace": hspace, "linewidth": linewidth})

    if render_type=='bracket':
        template_filename = 'tournaments/BracketDisplay.jinja'
    elif render_type=='submit':
        template_filename = 'tournaments/BracketFillout.jinja'
    elif render_type=='table':
        template_filename = 'tournaments/TablePositions.jinja'

    return render_template(template_filename,**render_vars)
