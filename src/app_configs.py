from flask import Blueprint, render_template, session, request, redirect
from database import database, get_database
import oauth
import random
import string
from page_tools import get_general_variables, generate_error


app_configs = Blueprint('app_configs', __name__)

@app_configs.route("/configs", methods=["GET", "POST"])
def configs():
    if "oauth_client_id" in request.form and "oauth_client_secret" in request.form:
        with database() as db:
            db["oauth_client_id"] = request.form["oauth_client_id"]
            db["oauth_client_secret"] = request.form["oauth_client_secret"]

    elif "general" in request.form and "administrators" in request.form and "baseurl" in request.form:
        baseurl = request.form["baseurl"]
        with database() as db:
            db["baseurl"] = baseurl[:-1] if baseurl.endswith("/") else baseurl
            db["admins"] = request.form["administrators"].splitlines()

    elif "save_project" in request.form and "project" in request.form and "administrators" in request.form:
        with database() as db:
            projects = db["projects"]
            projects[request.form["project"]]["administrators"] = request.form["administrators"].splitlines()
            db["projects"] = projects

    elif "update_project_oauth" in request.form and "project" in request.form:
        session["oauth_repository"] = request.form["project"]
        return redirect(oauth.get_url_authentification("repo:status"))

    elif "remove_project" in request.form and "project" in request.form:
        with database() as db:
            projects = db["projects"]
            del projects[request.form["project"]]
            db["projects"] = projects

    elif "repository" in request.form and "administrators" in request.form:
        session["oauth_repository"] = request.form["repository"]
        with database() as db:
            projects = db["projects"]
            projects[request.form["repository"]] = {
                "oauth_token": "",
                "name": request.form["repository"],
                "secret": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30)),
                "administrators": request.form["administrators"].splitlines(),
                "pr": dict()
            }
            db["projects"] = projects
        return redirect(oauth.get_url_authentification("repo:status"))

    db, view = get_general_variables("Configurations")

    if len(db["admins"]) > 0 and ("login" not in session or session["login"] not in db["admins"]):
        return generate_error("Access Forbidden")

    projects = db["projects"]
    for project in projects:
        projects[project]["administrators"] = "\n".join(projects[project]["administrators"] if "administrators" in projects[project] else list())
        if len(projects[project]["oauth_token"]) == 0:
            projects[project]["oauth_token"] = "NOT DEFINED!"

    view["baseurl"] = db["baseurl"]
    view["oauth_client_id"] = db["oauth_client_id"]
    view["oauth_client_secret"] = db["oauth_client_secret"]
    view["administrators"] = "\n".join(db["admins"])
    view["projects"] = projects

    return render_template("config.html", **view)
