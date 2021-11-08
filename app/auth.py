import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import models

bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'

#         # clean this up
#         if error is None:
#             try:
#                 user = models.User(username,generate_password_hash(password))
#                 user.insert()
#             except:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for('auth.login'))

#         flash(error)

#     return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = models.User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.user_id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.jinja')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = models.User.query.filter_by(user_id=user_id).first()


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
        usernames = models.User.query.with_entities(models.User.username).all()
        usernames = [u[0] for u in usernames]
        print(usernames)
        print(type(usernames[0]))
        if request.form['btn'] == 'Cambiar nombre de usuario':
            username = request.form['username']
            if username is None:
                error = 'Ingrese el nuevo usuario'
            elif username in usernames:
                error = 'El nombre de usuario ' + username + ' ya existe.'
            else:
                g.user.username = username
                models.db.session.commit()
                error = 'Su nuevo nombre de usuario es ' + username
        if request.form['btn'] == 'Cambiar contraseña':
            password = request.form['password']
            password2 = request.form['password2']
            if (password != password2) or (password is None):
                error = 'Error: ingrese la misma contraseña.'
            else:
                g.user.password = generate_password_hash(password)
                models.db.session.commit()
                error = 'Su contraseña ha sido actualizada.'

        flash(error)
    return render_template('auth/profile.jinja')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


