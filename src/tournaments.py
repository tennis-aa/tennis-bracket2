from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from datetime import datetime,timezone,timedelta

from . import dbfirestore
from . import auth

bp = Blueprint('tournaments', __name__)

@bp.route('/')
@auth.login_required
def index():
    user_entries = dbfirestore.db.collection("users").stream()
    users = {}
    for user_entry in user_entries:
        if user_entry.id == "usercount": continue
        user = user_entry.to_dict()
        users[user["user_id"]] = user["username"]

    tournament_docs = dbfirestore.db.collection("tournaments").stream()
    tournaments = [i.to_dict() for i in tournament_docs if i.id != "tournamentcount"]
    tournaments.sort(key = lambda x: x["start_time"],reverse=True)
    year_tournament_dict = {}
    for i in tournaments:
        tournament_info = {"name": i["name"]}
        table_results = i["results"]["table_results"]
        leaders = ""
        for j,position in enumerate(table_results["position"]):
            if position != 1:
                break
            if j != 0:
                leaders += "/"
            leaders += users[table_results["user"][j]]
        tournament_info["leader"] = leaders
        myindex = table_results["user"].index(g.user["user_id"])
        myposition = table_results["position"][myindex]
        tournament_info["myposition"] = myposition
        if i["year"] in year_tournament_dict:
            year_tournament_dict[i["year"]].append(tournament_info)
        else:
            year_tournament_dict[i["year"]] = [tournament_info]
    return render_template('index.jinja',year_tournament_dict=year_tournament_dict)

@bp.route('/<year>/<tournament>')
@auth.login_required
def bracket(year,tournament):
    tourn = dbfirestore.get_tournament(tournament,year)
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('index'))

    brack = dbfirestore.db.collection("brackets").where("tournament_id","==",tourn["tournament_id"]).stream()
    brack = [i.to_dict() for i in brack]
    user_ids = [i["user_id"] for i in brack]
    users = {}
    for i in user_ids:
        user = dbfirestore.db.collection("users").document(str(i)).get().to_dict()
        users[i] = user["username"]
    brackets = {}
    tzlocal = datetime.utcnow().astimezone().tzinfo
    localtime = datetime.now(tzlocal)
    if localtime < tourn["start_time"]:
        for i in brack:
            user = users[i["user_id"]]
            brackets.update({user: [-1]*tourn["bracketsize"]})
    else:
        for i in brack:
            user = users[i["user_id"]]
            brackets.update({user: [j for j in i["bracket"]]})

    results_dict = tourn["results"]
    results_dict['table_results']['user'] = [users[i] for i in results_dict['table_results']['user']]
    
    render_vars = {'bracketSize':tourn["bracketsize"],'players':tourn["players"],'brackets':brackets,
        'results_dict':results_dict}
    return bracketRender('bracket',year,tournament,render_vars)

@bp.route('/<year>/<tournament>/submit',methods=('GET','POST'))
@auth.login_required
def submit(year,tournament):
    tourn = dbfirestore.get_tournament(tournament,year)
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('index'))

    brack = dbfirestore.db.collection("brackets").where("tournament_id","==",tourn["tournament_id"]).where("user_id","==",g.user["user_id"]).get()
    if len(brack) == 1:
        brack = brack[0].to_dict()
        bracket = brack["bracket"]
    else:
        brack = None
        bracket = [-1]*(tourn["bracketsize"]-1)

    tzlocal = datetime.utcnow().astimezone().tzinfo
    localtime = datetime.now(tzlocal)
    time_to_start = tourn["start_time"] - localtime

    if request.method == 'GET':
        if time_to_start.total_seconds() <= 0:
            time_to_start = timedelta()
        render_vars = {'bracketSize':tourn["bracketsize"],'players':tourn["players"],
            'elos':tourn["elos"],'bracket':bracket, 'time_to_start':time_to_start}

        return bracketRender('submit',year,tournament,render_vars)
    elif request.method == 'POST':
        # The client side does not allow to make changes after begin of tournament, so the following if-block should never be reached
        if time_to_start.total_seconds() <= 0:
            flash('Las inscripciones estan cerradas.' if g.user["language"] == "spanish" else "Sign up is closed")
            return redirect(url_for("tournaments.submit",year=year,tournament=tournament))
        try:
            for i in range(tourn["bracketsize"]-1):
                try:
                    bracket[i] = int(request.form['select{}'.format(tourn["bracketsize"]+i)])
                except:
                    pass
            if brack is None:
                dbfirestore.add_bracket(g.user["user_id"],tourn["tournament_id"],bracket)
                flash('Su cuadro ha sido creado exitosamente' if g.user["language"] == "spanish" else 'Your entry has been created successfully')
            else:
                dbfirestore.update_bracket(brack["bracket_id"], {"bracket" : bracket})
                flash('Su cuadro ha sido actualizado exitosamente' if g.user["language"] == "spanish" else 'Your bracket has been updated successfully')
        except:
            flash("Hubo un error guradando su cuadro. Contacte al administrador." if g.user["language"] == "spanish" else 'There was an error saving your bracket. Contact the maintainer.')
        return redirect(url_for("tournaments.submit",year=year,tournament=tournament))
    else:
        return redirect(url_for('index'))

@bp.route('/<year>/<tournament>/table')
@auth.login_required
def table(year,tournament):
    tourn = dbfirestore.get_tournament(tournament,year)
    if tourn is None:
        flash('could not find tournament')
        return redirect(url_for('index'))

    users = {}
    for i in tourn["results"]['table_results']['user']:
        user = dbfirestore.db.collection("users").document(str(i)).get().to_dict()
        users[i] = user["username"]

    tourn["results"]['table_results']['user'] = [users[i] for i in tourn["results"]['table_results']['user']]

    tzlocal = datetime.utcnow().astimezone().tzinfo
    localtime = datetime.now(tzlocal)
    time_to_start = tourn["start_time"] - localtime

    render_vars = {'bracketSize': tourn["bracketsize"],'table_results': tourn["results"]['table_results'],
        "year": year, "tournament": tournament, "seconds_to_start": time_to_start.total_seconds()}
    return render_template("tournaments/TablePositions.jinja",**render_vars)

@bp.route('/<year>/<tournament>/<id>/bracket')
@auth.login_required
def bracket_json(year,tournament,id):
    tourn = dbfirestore.get_tournament(tournament,year)
    if tourn is None:
        return []

    brack = dbfirestore.db.collection("brackets").where("tournament_id","==",tourn["tournament_id"]).where("user_id","==",int(id)).get()
    if len(brack) == 1:
        brack = brack[0].to_dict()
        bracket = brack["bracket"]
        return bracket
    else:
        return []

import math
def bracketRender(render_type,year,tournament,render_vars):
    bracketSize = render_vars['bracketSize']
    rounds = math.log(bracketSize,2)
    if not rounds.is_integer():
            raise ValueError("bracketSize has to be 2^n")
    rounds = int(rounds)

    # input variables
    counter = [0]*(rounds+1)
    for j in range(rounds):
        counter[j+1] = counter[j] + int(bracketSize/(2**j))

    try:
        time_to_start = render_vars['time_to_start']
    except:
        time_to_start = timedelta()

    hours_to_start = time_to_start.days*24 + time_to_start.seconds//3600
    minutes_to_start = (time_to_start.seconds//60)%60

    render_vars.update({"rounds" : rounds, "counter" : counter, "year" : year, "tournament": tournament,
    "hours_to_start":hours_to_start,"minutes_to_start":minutes_to_start})

    if render_type=='bracket':
        template_filename = 'tournaments/BracketDisplay.jinja'
    elif render_type=='submit':
        template_filename = 'tournaments/BracketFillout.jinja'

    return render_template(template_filename,**render_vars)

