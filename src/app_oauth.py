from flask import Blueprint, redirect, url_for, session
import oauth
from database import database
from page_tools import generate_error


app_oauth = Blueprint('app_oauth', __name__)

@app_oauth.route("/callback/oauth")
def callback_oauth():
    if "oauth_repository" in session:
        access_token = oauth.get_access_token()
        if access_token:
            with database() as db:
                projects = db["projects"]
                projects[session["oauth_repository"]]["oauth_token"] = access_token
                db["projects"] = projects
            session.pop("oauth_repository", None)
            return redirect(url_for("app_configs.configs"))
        return generate_error("[OAuth Repository] Bad access token")
    elif oauth.authenticate():
        redirect_url = url_for("app_project.home")
        if "redirect_url" in session:
            redirect_url = session["redirect_url"]
            session.pop("redirect_url", None)
        return redirect(redirect_url)
    return generate_error("[OAuth General] Bad access token")
