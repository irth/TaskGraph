from flask import Blueprint, render_template

blueprint = Blueprint('sources', __name__)


@blueprint.route("/add")
def add():
    return render_template('add.html')
