from threading import Lock
from contextlib import contextmanager
import json

@contextmanager
def database():
    data = dict()
    mutex = Lock()
    mutex.acquire()
    db = dict()
    try:
        with open("database.json", "r") as f:
            db = json.load(f)
    except:
        pass
    if "baseurl" not in db:
        db["baseurl"] = ""
    if "admins" not in db:
        db["admins"] = list()
    if "oauth_client_id" not in db:
        db["oauth_client_id"] = ""
    if "oauth_client_secret" not in db:
        db["oauth_client_secret"] = ""
    if "projects" not in db:
        db["projects"] = dict()
    yield db
    with open("database.json", "w") as f:
        json.dump(db, f)
    mutex.release()

def get_database():
    data = None
    with database() as db:
        data = dict(db)
    return data
