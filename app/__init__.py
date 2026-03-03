import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Point Flask to your SQLite DB file
    # (Absolute path avoids “works on my machine” path issues)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config["DATABASE"] = os.path.join(project_root, "data", "armor.db")

    from .db import init_app as init_db
    init_db(app)

    from .api import bp as api_bp
    app.register_blueprint(api_bp)

    return app