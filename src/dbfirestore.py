from firebase_admin import initialize_app, firestore

default_app = initialize_app()
db = firestore.client()

'''
setup_db(app):
    in case the app database needs setup for the app
'''
def setup_db(app):
    pass

def add_user(username, password, language):
    coll = db.collection("users")
    doc_usercount = coll.document("usercount")
    usercount = doc_usercount.get().to_dict()["count"]
    usercount += 1
    doc_usercount.update({"count": usercount})

    doc_user = coll.document(str(usercount))
    doc_user.set({"user_id": usercount,
                  "username": username,
                  "password": password,
                  "language": language})

def update_user(id,username=None,password=None,language=None):
    coll = db.collection("users")
    doc_user = coll.document(str(id))
    existing_user = doc_user.get().to_dict()
    if existing_user is not None:
        if username is None: username = existing_user["username"]
        if password is None: password = existing_user["password"]
        if language is None: language = existing_user["language"]
        doc_user.update({"user_id": id,
                  "username": username,
                  "password": password,
                  "language": language})
        return True
    else:
        return False

def add_tournament(name,year,start_time,end_time,points_per_round,atplink,
        bracketsize,surface,sets,players,elos,utrs,results):
    coll = db.collection("tournaments")
    doc_tournamentcount = coll.document("tournamentcount")
    tournamentcount = doc_tournamentcount.get().to_dict()["count"]
    tournamentcount += 1
    doc_tournamentcount.update({"count": tournamentcount})

    data = {
        "tournament_id" : tournamentcount,
        "name" : name,
        "year" : year,
        "start_time" : start_time,
        "end_time" : end_time,
        "points_per_round" : points_per_round,
        "atplink" : atplink,
        "bracketsize" : bracketsize,
        "surface" : surface,
        "sets" : sets,
        "players" : players,
        "elos" : elos,
        "utrs" : utrs,
        "results" : results
    }
    doc_tournament = coll.document(str(tournamentcount))
    doc_tournament.set(data)

def update_tournament(data):
    coll = db.collection("tournaments")
    doc_tournament = coll.document(str(data["tournament_id"]))
    for key in data:
        if key not in [
                "tournament_id",
                "name",
                "year",
                "start_time",
                "end_time",
                "points_per_round",
                "atplink",
                "bracketsize",
                "surface",
                "sets",
                "players",
                "elos",
                "utrs",
                "results"]:
            print(key, " is not in tournament data")
            return False
    doc_tournament.update(data)
    return True

def get_tournament(name,year):
    coll = db.collection("tournaments")
    query = coll.where("name","==",name).where("year","==",int(year))
    tourn = query.get()
    if len(tourn) == 1:
        return tourn[0].to_dict()
    else:
        return None

def add_bracket(user_id,tournament_id,bracket):
    usercount = db.collection("users").document("usercount").get().to_dict()["count"]
    tournamentcount = db.collection("tournaments").document("tournamentcount").get().to_dict()["count"]
    if user_id < 1 or user_id > usercount or tournament_id < 1 or tournament_id > tournamentcount:
        print("user_id or tournament_id out of range")
    coll = db.collection("brackets")
    doc_bracketcount = coll.document("bracketcount")
    bracketcount = doc_bracketcount.get().to_dict()["count"]
    bracketcount += 1
    doc_bracketcount.update({"count": bracketcount})

    data = {
        "bracket_id" : bracketcount,
        "user_id" : user_id,
        "tournament_id" : tournament_id,
        "bracket" : bracket
    }
    doc_bracket = coll.document(str(bracketcount))
    doc_bracket.set(data)

def update_bracket(id,data):
    coll = db.collection("brackets")
    doc_bracket = coll.document(str(id))
    for key in data:
        if key != "bracket":
            print(key, " is not in bracket data or cannot be updated")
            return False
    doc_bracket.update(data)
    return True