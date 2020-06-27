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

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_username(username):
        if len(username) < 2:
            return ['The username needs to be at least 2 characters long.']

        valid = string.ascii_letters + string.digits
        for ch in username:
            if ch not in valid:
                return ['The username can only contain ASCII letters and numbers.']

        return []

    @staticmethod
    def validate_password(password, repeat):
        if len(password) < 10:
            return ['The password needs to be at least 10 characters long.']

        if password != repeat:
            return ['The passwords do not match.']

        return []


if __name__ == '__main__':
    print("Creating db...")
    from main import app
    with app.app_context():
        db.create_all()
