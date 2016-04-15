from flask import render_template, session
from database import get_database
from urllib.parse import urlencode


def get_general_variables(title):
    db = get_database()
    login = session["login"] if "login" in session else None
    is_admin = login in db["admins"] or len(db["admins"]) == 0
    my_projects = list()
    for project in db["projects"]:
        if is_admin or login in db["projects"][project]["administrators"]:
            my_projects.append({
                "link": "/?" + urlencode({"project": project}),
                "name": project,
                "administrators_list": ", ".join(db["projects"][project]["administrators"])
            })
    view = {
        "title": title,
        "login": login,
        "is_admin": is_admin,
        "my_projects": my_projects,
        "baseurl": db["baseurl"]
    }
    return db, view

def generate_error(message, view=None, code=400):
    if not view:
        _, view = get_general_variables("Error")
    view["error"] = message
    return render_template("error.html", **view), code
