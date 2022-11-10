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
        error = None
        docs = dbfirestore.db.collection("users").where("username","==",username).stream()
        for doc in docs:
            user = doc.to_dict()
            break # only one user should be found anyway. we return the first

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
            usernames = [i["username"] for i in docs]
            if username is None:
                message = 'Ingrese el nuevo usuario'
            elif username in usernames:
                message = 'El nombre de usuario ' + username + ' ya existe.'
            else:
                g.user["username"] = username
                dbfirestore.update_user(g.user["user_id"],username)
                message = 'Su nuevo nombre de usuario es ' + username
        elif "password" in request.form:
            password = request.form['password']
            password2 = request.form['password2']
            if (password != password2) or (password is None):
                message = 'Error: ingrese la misma contraseña.'
            else:
                g.user["password"] = generate_password_hash(password)
                dbfirestore.update_user(g.user["user_id"],password=g.user["password"])
                message = 'Su contraseña ha sido actualizada.'
        elif "language" in request.form:
            language = request.form['language']
            if language in ["spanish","english"]:
                g.user["language"] = language
                dbfirestore.update_user(g.user["user_id"],language=language)
                message = 'Su idioma ha sido actualizado'
            else:
                message = "Idioma no disponible"
        else:
            message = "Error enviando la informacion al servidor"

        flash(message)
    return render_template('auth/profile.jinja')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


