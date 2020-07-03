from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

import caldav

from models import TasklistSource, Tasklist, db

blueprint = Blueprint('sources', __name__)

# TODO: make abstract source class


class CalDAVSource:
    def __init__(self, url, username, password):
        self.client = caldav.DAVClient(
            url, username=username, password=password)

    def tasklists(self):
        # TODO: firure out how to update the tasklists list periodically
        tasklists = []
        try:
            # TODO: invalid passwords could cause long delays
            # In case of an invalid password this could take a long time.
            # Investigate into timeouts and maybe later mark as invalid whenever
            # a request fails, to avoid making any further requests until the
            # user updates the auth information.
            principal = self.client.principal()
            for calendar in principal.calendars():
                tasklist = Tasklist(name=calendar.name,
                                    remote_id=str(calendar.url))
                tasklists.append(tasklist)
                # TODO: count todos? or maybe this should be separate, as a cron job
        except caldav.lib.error.AuthorizationError:
            # TODO: mark as problematic
            return [], "Invalid username or password."
        except:
            return [], "Unknown error, make sure the url/username/password are correct or try again later."
        return tasklists, None


@blueprint.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        # TODO: forbid from calling local adresses somehow
        name = request.form["name"]

        url = request.form["caldav"]
        username = request.form.get("username", "")
        password = request.form.get("caldav_password", "")

        if len(name) == 0:
            return render_template('add.html', caldav=url, username=username, name=name, name_error="Name cannot be empty.")

        if len(url) == 0:
            return render_template('add.html', caldav=url, username=username, name=name, caldav_error="URL cannot be empty.")

        src = CalDAVSource(url, username, password)
        tasklists, error = src.tasklists()
        if error is not None:
            flash(error, "error")
            return render_template('add.html', caldav=url, username=username, name=name)

        src_model = TasklistSource(
            name=name,
            user=current_user,
            source="caldav",
            url=url, username=username, password=password)

        for tasklist in tasklists:
            tasklist.source = src_model

        db.session.add_all([src_model, *tasklists])
        db.session.commit()
        # TODO: do we need to catch exceptions and do rollbacks?

        return "OK"
