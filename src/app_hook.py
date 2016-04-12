from flask import Blueprint, request
from database import database, get_database
import hmac
import hashlib
from validations import set_status


app_hook = Blueprint('app_hook', __name__)

def verify_hmac_hash(secret, data, signature):
    mac = hmac.new(bytes(secret, "UTF-8"), msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest("sha1=" + mac.hexdigest(), signature)

@app_hook.route("/callback/hook", methods=['POST'])
def callback_hook():
    if request.headers.get('X-GitHub-Event') == "ping":
        return '{"message": "pong"}'

    if request.headers.get('X-GitHub-Event') == "pull_request":
        data = request.get_json()
        repository_name = data["repository"]["full_name"]
        db = get_database()
        if repository_name not in db["projects"]:
            return '{"message": "Project not found"}', 404
        project = db["projects"][repository_name]
        if not verify_hmac_hash(project["secret"], request.data, request.headers.get("X-Hub-Signature")):
            return '{"message": "Bad signature"}', 403
        pr_number = data["pull_request"]["number"]
        pr_state = data["pull_request"]["state"]
        pr_title = data["pull_request"]["title"]
        pr_link = data["pull_request"]["html_url"]
        pr_statuses_url = data["pull_request"]["statuses_url"]
        create_status = False
        with database() as db:
            projects = db["projects"]
            if pr_number in projects[repository_name]["pr"]:
                projects[repository_name]["pr"][pr_number]["state"] = pr_state
                projects[repository_name]["pr"][pr_number]["title"] = pr_title
                projects[repository_name]["pr"][pr_number]["link"] = pr_link
                if projects[repository_name]["pr"][pr_number]["statuses_url"] != pr_statuses_url:
                    projects[repository_name]["pr"][pr_number]["statuses_url"] = pr_statuses_url
                    projects[repository_name]["pr"][pr_number]["validations"] = dict()
                    create_status = True
            else:
                create_status = True
                projects[repository_name]["pr"][pr_number] = {
                    "number": pr_number,
                    "state": pr_state,
                    "title": pr_title,
                    "link": pr_link,
                    "statuses_url": pr_statuses_url,
                    "validations": dict()
                }
            project = projects[repository_name]
            db["projects"] = projects
        if create_status:
            set_status(db["baseurl"], project, pr_number)
        return '{"message": "Success"}'

    return '{"message": "Unknown event"}', 400
