from threading import Lock
import shelve
from contextlib import contextmanager

@contextmanager
def database():
    data = dict()
    mutex = Lock()
    mutex.acquire()
    db = shelve.open("database.shelve")
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
    print("close db", dict(db))
    db.close()
    mutex.release()

def get_database():
    data = dict()
    fields = ["baseurl", "admins", "oauth_client_id", "oauth_client_secret", "projects"]
    with database() as db:
        for field in fields:
            data[field] = db[field]
    return data
