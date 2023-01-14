import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import dbfirestore

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        docs = dbfirestore.db.collection("users").where("username","==",username).stream()
        user = None
        for doc in docs:
            user = doc.to_dict()
            break # only one user should be found anyway. we return the first

        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user["password"], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user["user_id"]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.jinja')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = dbfirestore.db.collection("users").document(str(user_id)).get().to_dict()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    if request.method == 'POST':
        if "username" in request.form:
            username = request.form['username']
            docs = dbfirestore.db.collection("users").stream()
            usernames = [i.to_dict()["username"] for i in docs if i.id != "usercount"]
            if username is None:
                message = 'Ingrese el nuevo nombre de usuario' if g.user["language"] == "spanish" else "Enter new username"
            elif username in usernames:
                message = ('El nombre de usuario ' + username + ' ya existe.') if g.user["language"] == "spanish" else ('The username ' + username + ' already exists')
            else:
                g.user["username"] = username
                dbfirestore.update_user(g.user["user_id"],username)
                message = ('Su nuevo nombre de usuario es ' + username) if g.user["language"] == "spanish" else ('Your new username is ' + username)
        elif "password" in request.form:
            password = request.form['password']
            password2 = request.form['password2']
            if (password != password2) or (password is None):
                message = 'Error: ingrese la misma contraseña.' if g.user["language"] == "spanish" else 'Error: enter the same password'
            else:
                g.user["password"] = generate_password_hash(password)
                dbfirestore.update_user(g.user["user_id"],password=g.user["password"])
                message = 'Su contraseña ha sido actualizada' if g.user["language"] == "spanish" else 'Your password has been updated'
        elif "language" in request.form:
            language = request.form['language']
            if language in ["spanish","english"]:
                g.user["language"] = language
                dbfirestore.update_user(g.user["user_id"],language=language)
                message = 'Su idioma ha sido actualizado' if g.user["language"] == "spanish" else 'Your language has been updated'
            else:
                message = "Idioma no disponible" if g.user["language"] == "spanish" else 'Language not supported'
        else:
            message = "Error enviando la informacion al servidor" if g.user["language"] == "spanish" else "Error sending information to server"

        flash(message)
    return render_template('auth/profile.jinja')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


