from flask import session, request
import requests
from urllib.parse import urlencode
import random
import string
from database import get_database

def is_connected():
    if "login" in session:
        return True
    session["redirect_url"] = request.path + "?" + urlencode(request.args)
    return False

def get_url_authentification(scope=""):
    session["oauth_state"] = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
    db = get_database()
    payload = {
        "client_id": db["oauth_client_id"],
        "scope": scope,
        "state": session["oauth_state"]
    }
    url_authentification = "https://github.com/login/oauth/authorize?" + urlencode(payload)
    return url_authentification

def get_access_token():
    if "code" not in request.args or "state" not in request.args:
        return None
    if "oauth_state" not in session or session["oauth_state"] != request.args["state"]:
        return None
    db = get_database()
    payload = {
        "client_id": db["oauth_client_id"],
        "client_secret": db["oauth_client_secret"],
        "code": request.args["code"],
        "state": request.args["state"]
    }
    response = requests.post("https://github.com/login/oauth/access_token", params=payload, headers={'Accept': 'application/json'}).json()
    if "access_token" in response:
        return response["access_token"]
    return None

def authenticate():
    access_token = get_access_token()
    if access_token:
        user = requests.get("https://api.github.com/user", params={"access_token": access_token}).json()
        session["login"] = user["login"]
        return True
    return False
