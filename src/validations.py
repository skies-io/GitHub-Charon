from urllib.parse import urlencode
import requests


def get_state_validation(validations, minimum_acceptances=2):
    accepted = list()
    refused = list()
    forced = list()
    for admin in validations:
        if validations[admin]["force"] == True:
            forced.append(admin)
        elif validations[admin]["accept"] == True:
            accepted.append(admin)
        else:
            refused.append(admin)
    if len(forced) > 0:
        return "forced", forced
    if len(refused) > 0:
        return "refused", refused
    if len(accepted) >= minimum_acceptances:
        return "accepted", accepted
    return "pending", accepted

def set_status(baseurl, project, pr_number):
    def general_message(admins, accepted=True):
        names = ""
        if len(admins) == 1:
            names = admins[0]
        else:
            names = ", ".join(admins[:-1])
            names = " and ".join([names, admins[-1]])
        action = "accepted" if accepted else "refused"
        return names + " " + action + " the Pull Request."

    pr = project["pr"][pr_number]
    state_validation, admins = get_state_validation(pr["validations"])

    if state_validation == "forced":
        state = "success"
        description = admins[0] + " forced the validation: " + pr["validations"][admins[0]]["message"]
    elif state_validation == "refused":
        state = "failure"
        description = general_message(admins, accepted=False)
    elif state_validation == "accepted":
        state = "success"
        description = general_message(admins, accepted=True)
    else:
        state = "pending"
        description = general_message(admins, accepted=True)

    data = {
        "state": state,
        "target_url": baseurl + "/?" + urlencode({"project": project["name"], "pr": pr_number}),
        "description": description,
        "context": "GitHub-Charon"
    }

    response = requests.post(pr["statuses_url"], json=data, headers={"Authorization": "token " + project["oauth_token"]})

    return response.status_code >= 200 and response.status_code < 300
