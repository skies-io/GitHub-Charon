from flask import Flask
import os

from app_configs import app_configs
from app_hook import app_hook
from app_oauth import app_oauth
from app_project import app_project


app = Flask(__name__)

app.secret_key = os.urandom(24)

app.register_blueprint(app_configs)
app.register_blueprint(app_hook)
app.register_blueprint(app_oauth)
app.register_blueprint(app_project)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
