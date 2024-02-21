from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from statistics import mean, median

from . import dbfirestore
from . import auth

bp = Blueprint('stats', __name__, url_prefix="/stats")

@bp.route('/')
@auth.login_required
def index():
    tournament_docs = dbfirestore.db.collection("tournaments").stream()
    tournaments = [i.to_dict() for i in tournament_docs if i.id != "tournamentcount"]
    users = dbfirestore.get_user_dict()

    u = user_stats(tournaments,g.user["user_id"])
    y = yearly_stats(tournaments,users)

    return render_template('stats/index.jinja',user_stats=u, yearly_stats = y, users=users)

def user_stats(tournaments, user_id):
    tournament_docs = dbfirestore.db.collection("tournaments").stream()
    tournaments = [i.to_dict() for i in tournament_docs if i.id != "tournamentcount"]
    years = []
    positions = []
    first = []
    last = []
    for t in tournaments:
        try:
            table_results = t["results"]["table_results"]
            ind = table_results["user"].index(user_id)
            years.append(t["year"])
            positions.append(table_results["position"][ind])
            first.append(positions[-1] == 1)
            last.append(positions[-1] == max(table_results["position"]))
        except ValueError:
            pass
    if len(years) == 0:
        return {}

    stats = {}
    stats["overall"] = {"n": len(positions),
        "mean_pos": mean(positions),
        "median_pos": median(positions),
        "first": sum(first),
        "last": sum(last)
        }
    years_unique = list(set(years))
    years_unique.sort(reverse=True)
    for year in years_unique:
        ind = [y == year for y in years]
        p = [i for (i,v) in zip(positions,ind) if v]
        f = [i for (i,v) in zip(first,ind) if v]
        l = [i for (i,v) in zip(last,ind) if v]
        stats[str(year)] = {
            "n": len(p),
            "mean_pos": mean(p),
            "median_pos": median(p),
            "first": sum(f),
            "last": sum(l)
            }
    return stats


def yearly_stats(tournaments, users):
    years = list(set([t["year"] for t in tournaments]))
    years.sort(reverse=True)
    years.insert(0,"overall")
    table = {}
    for year in years:
        table[str(year)] = {}
        for user in users:
            table[str(year)][user] = {
                "n": 0,
                "first": 0,
                "last": 0
            }

    for t in tournaments:
        table_results = t["results"]["table_results"]
        year = str(t["year"])
        for i, user in enumerate(table_results["user"]):
            table[year][user]["n"] += 1
            table["overall"][user]["n"] += 1
            if table_results["position"][i] == 1:
                table[year][user]["first"] += 1
                table["overall"][user]["first"] += 1
            elif table_results["position"][i] == max(table_results["position"]):
                table[year][user]["last"] += 1
                table["overall"][user]["last"] += 1

    # remove entries without any participations
    remove = []
    for year in table:
        for user in table[year]:
            if table[year][user]["n"] == 0:
                remove.append((year,user))
    for y,u in remove:
        table[y].pop(u)

    return table
