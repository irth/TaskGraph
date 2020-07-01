from flask import Blueprint, render_template, request, flash

import caldav

blueprint = Blueprint('sources', __name__)

# TODO: make abstract source class


class CalDAVSource:
    def __init__(self, url, username, password):
        self.client = caldav.DAVClient(
            url, username=username, password=password)

    def validate(self):
        try:
            # TODO: invalid passwords could cause long delays
            # In case of an invalid password this could take a long time.
            # Investigate into timeouts and maybe later mark as invalid whenever
            # a request fails, to avoid making any further requests until the
            # user updates the auth information.
            self.client.principal()
        except caldav.lib.error.AuthorizationError:
            return "Invalid username or password."
        except:
            return "Unknown error, make sure the url/username/password are correct or try again later."


@blueprint.route("/add", methods=["GET", "POST"])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        # TODO: forbid from calling local adresses somehow
        url = request.form["caldav"]
        username = request.form.get("username", "")
        password = request.form.get("caldav_password", "")
        src = CalDAVSource(url, username, password)
        error = src.validate()
        if error is None:
            return "OK"  # TODO: add to db
        else:
            flash(error, "error")
            return render_template('add.html', caldav=url, username=username)
