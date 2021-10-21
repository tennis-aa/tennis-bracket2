import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import models

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    # configure database
    models.setup_db(app)
    # models.db_drop_and_create_all()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # page to register and login
    from . import auth
    app.register_blueprint(auth.bp)

    # index page with list of tournaments
    from . import tournaments
    app.register_blueprint(tournaments.bp)
    app.add_url_rule('/', endpoint='index')

    return app