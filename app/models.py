import os
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, TIMESTAMP
from flask_sqlalchemy import SQLAlchemy
from .password import password

db = SQLAlchemy()

'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_name ='tennis_bracket'
    default_database_path= "postgresql://{}:{}@{}/{}".format('postgres', password, 'localhost:5432', database_name)
    database_path = os.getenv('DATABASE_URL', default_database_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

class User(db.Model):
    __tablename__ = 'user_pass'
    user_id = Column(Integer(), primary_key=True)
    username = Column(Text(), unique=True)
    password = Column(Text())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def details(self):
        return {
            'id': self.id,
            'user': self.username,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

class Tournament(db.Model):
    __tablename__ = "tournaments"
    tournament_id = Column(Integer, primary_key=True)
    name = Column(Text())
    year = Column(Integer())
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    points_per_round = Column(JSON())
    atplink = Column(Text())
    bracketsize = Column(Integer())
    surface = Column(Text())
    sets = Column(Integer())
    players = Column(JSON())
    elos = Column(JSON())
    results = Column(JSON())

class BracketModel(db.Model):
    __tablename__ = "brackets"
    bracket_id = Column(Integer(),primary_key=True)
    user_id = Column(Integer(),ForeignKey(User.user_id))
    tournament_id = Column(Integer(),ForeignKey(Tournament.tournament_id))
    bracket = Column(JSON())

    def __init__(self,user_id,tournament_id,bracket):
        self.user_id = user_id
        self.tournament_id = tournament_id
        self.bracket = bracket