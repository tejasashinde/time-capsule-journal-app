from flask import Flask

from .auth import auth_bp
from .config import Config
from .db import close_db, init_app
from .main import main_bp
from .oauth import init_oauth


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app)
    init_oauth(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    app.teardown_appcontext(close_db)

    return app
