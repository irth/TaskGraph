import string

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()


def init_app(app):
    db.init_app(app)
    bcrypt.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, unique=False, nullable=False)
    sources = db.relationship('TasklistSource', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_username(username):
        if len(username) < 2:
            return 'The username needs to be at least 2 characters long.'

        valid = string.ascii_letters + string.digits
        for ch in username:
            if ch not in valid:
                return 'The username can only contain ASCII letters and numbers.'

        return None

    @staticmethod
    def validate_password(password, repeat):
        if len(password) < 10:
            return 'The password needs to be at least 10 characters long.'

        if password != repeat:
            return 'The passwords do not match.'

        return None


class TasklistSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    source = db.Column(db.String)  # source type, only caldav for now
    name = db.Column(db.String)  # a human-readable name, chosen by the user

    url = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)

    # for any additional data, handled by the source implementation
    other = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tasklists = db.relationship("Tasklist", backref="source", lazy=True)


class Tasklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    remote_id = db.Column(db.String)  # for caldav, this is the url

    source_id = db.Column(db.Integer, db.ForeignKey(
        'tasklist_source.id'), nullable=False)
