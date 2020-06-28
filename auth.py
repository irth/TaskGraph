from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from models import User, db

blueprint = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


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
    flash('Logged out.', 'success')
    return redirect(url_for('root'))


def login_fail(username):
    flash(u'Incorrect username or password', 'error')
    return render_template('login.html', username=username)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def do_login():
    username = request.form['username']
    password = request.form['password']

    if len(username) == 0 or len(password) == 0:
        return login_fail(username)

    u = User.query.filter_by(username=username).first()
    if u is None:
        return login_fail(username)
    if not u.check_password(password):
        return login_fail(username)

    login_user(u, remember=True)
    flash(u'Logged in successfully.', 'success')
    next = request.args.get('next')
    if not is_safe_url(next):
        return abort(400)

    return redirect(next or url_for('root'))


def do_register():
    username = request.form['username']
    password = request.form['password']
    repeat = request.form['repeat']

    username_error = User.validate_username(username)
    password_error = User.validate_password(password, repeat)

    if username_error is not None or password_error is not None:
        return render_template('login.html', register=True, username_error=username_error, password_error=password_error, username=username)

    u = User(username=username)
    u.set_password(password)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template('login.html', register=True, username_error='Username already taken.', password_error=password_error)
    login_user(u, remember=True)
    flash(u'Registered successfully.', 'success')
    return redirect(url_for('root'))
