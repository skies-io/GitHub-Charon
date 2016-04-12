from urllib.parse import urlencode
import requests


def get_state_validation(validations):
    number_accepted = 0
    number_refused = 0
    for admin in validations:
        if validations[admin]["force"] == True:
            return "forced", admin
        elif validations[admin]["accept"] == True:
            number_accepted += 1
        else:
            number_refused += 1
    if number_refused > 0:
        return "refused", number_refused
    if number_accepted >= 2:
        return "accepted", number_accepted
    return "pending", number_accepted

def set_status(baseurl, project, pr_number):
    def general_message(number, accepted=True):
        admins = str(number) + " administrator" + ("s" if number > 1 else "")
        action = "accepted" if accepted else "refused"
        return admins + " " + action + " the Pull Request."

    pr = project["pr"][pr_number]
    state_validation, number = get_state_validation(pr["validations"])

    if state_validation == "forced":
        state = "success"
        description = number + " forced the validation: " + pr["validations"][number]["message"]
    elif state_validation == "refused":
        state = "failure"
        description = general_message(number, accepted=False)
    elif state_validation == "accepted":
        state = "success"
        description = general_message(number, accepted=True)
    else:
        state = "pending"
        description = general_message(number, accepted=True)

    data = {
        "state": state,
        "target_url": baseurl + "/?" + urlencode({"project": project["name"], "pr": pr_number}),
        "description": description,
        "context": "pr-validation"
    }
    requests.post(pr["statuses_url"], json=data, headers={"Authorization": "token " + project["oauth_token"]})
