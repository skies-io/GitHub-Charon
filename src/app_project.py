from flask import Blueprint, render_template, redirect, url_for, request, session
import oauth
from database import database
from urllib.parse import urlencode
from validations import get_state_validation, set_status
from page_tools import get_general_variables, generate_error


app_project = Blueprint('app_project', __name__)


def get_view_info_pr(project_name, pull_request):
    state_validation, _ = get_state_validation(pull_request["validations"])
    user_validation = None
    if "login" in session and session["login"] in pull_request["validations"]:
        user_validation = pull_request["validations"][session["login"]]["action"]
    return {
        "number": int(pull_request["number"]),
        "state": pull_request["state"],
        "title": pull_request["title"],
        "github_link": pull_request["link"],
        "link": "/?" + urlencode({"project": project_name, "pr": pull_request["number"]}),
        "state_validation": state_validation,
        "user_validation": user_validation,
        "validations": pull_request["validations"]
    }


@app_project.route("/", methods=["GET", "POST"])
def home():
    db, view = get_general_variables("Home")

    if len(db["admins"]) == 0:
        return redirect(url_for("app_configs.configs"))

    if not oauth.is_connected():
        return redirect(oauth.get_url_authentification("repo:status"))

    if "project" not in request.args:
        return render_template("main.html", **view)

    if request.args["project"] not in db["projects"]:
        return generate_error("Project not found", view=view)

    project = db["projects"][request.args["project"]]

    if view["login"] not in project["administrators"]:
        return generate_error("Access Forbidden", view=view, code=403)

    view["title"] = "Project " + project["name"]

    if "pr" not in request.args:
        pr = list()
        for pr_number in project["pr"]:
            pr.append(get_view_info_pr(project["name"], project["pr"][pr_number]))
        view["pr"] = sorted(pr, key=lambda elem: elem["number"], reverse=True)

        return render_template("project.html", **view)

    pr_number = request.args["pr"]
    if pr_number not in project["pr"]:
        return generate_error("Pull request not found", view=view)

    if "message" in request.form:
        if project["pr"][pr_number]["state"] != "open" and "acknowledge" not in request.form:
            view["error_validation"] = "Pull request already closed."
        elif "accept" in request.form or "force" in request.form or "refuse" in request.form or "acknowledge" in request.form:
            action = "unknown"
            if "accept" in request.form:
                action = "accepted"
            elif "force" in request.form:
                action = "forced"
            elif "refuse" in request.form:
                action = "refused"
            elif "acknowledge" in request.form:
                action = "acknowledged"
            validation = {
                "action": action,
                "message": request.form["message"]
            }
            with database() as db:
                projects = db["projects"]
                projects[request.args["project"]]["pr"][pr_number]["validations"][view["login"]] = validation
                project["pr"][pr_number]["validations"][view["login"]] = validation
                db["projects"] = projects
            if not set_status(view["baseurl"], project, pr_number):
                view["error_validation"] = "Impossible to set status on GitHub."

    view["title"] += ", Pull Request #" + pr_number
    view["pr"] = get_view_info_pr(project["name"], project["pr"][pr_number])
    view["project_admins"] = project["administrators"]

    return render_template("pull_request.html", **view)
