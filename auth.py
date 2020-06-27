from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from models import User, db

blueprint = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def init_app(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return do_login()


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('login.html', register=True)
    else:
        return do_register()


@blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('root'))


def login_fail(username):
    return render_template('login.html', failed=True, username=username)


def do_login():
    username = request.form['username']
    password = request.form['password']
    remember = request.form.get('remember', '0') == "1"

    if len(username) == 0 or len(password) == 0:
        return login_fail(username)

    u = User.query.filter_by(username=username).first()
    if u is None:
        return login_fail(username)
    if not u.check_password(password):
        return login_fail(username)

    login_user(u, remember=remember)
    return redirect(url_for('root'))


def do_register():
    username = request.form['username']
    password = request.form['password']
    repeat = request.form['repeat']

    username_errors = User.validate_username(username)
    password_errors = User.validate_password(password, repeat)

    if len(username_errors) + len(password_errors) > 0:
        return render_template('login.html', register=True, username_errors=username_errors, password_errors=password_errors, username=username)

    u = User(username=username)
    u.set_password(password)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template('login.html', register=True, username_errors=['Username already taken.'], password_errors=password_errors)
