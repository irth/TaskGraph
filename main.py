import string

from flask import Flask, render_template, request, flash

import models
import auth

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.sqlite"
app.config["SECRET_KEY"] = "2137 papiez"

app.register_blueprint(auth.blueprint)

models.init_app(app)
auth.init_app(app)


@app.route('/')
def root():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
