import logging
from datetime import datetime

from flask import Flask, Blueprint

# from flask_cors import CORS
from flask_migrate import Migrate

import src.app.db.model as models
from src.extensions import db, jwt
from src.app.api import api
from src.app.api.healthz import ns_healthz
from src.app.api.user import ns_user
from src.app.api.auth import ns_auth
from src.app.api.role import ns_role
from src.config import config, Config


def create_app(config_name="default"):
    app = Flask(__name__, static_url_path="/public", static_folder="public")

    # load configurations object
    app.config.from_object(config[config_name])

    # database initialization
    db.init_app(app)
    migrate = Migrate(app, db)

    # initialize jwt
    jwt.init_app(app)

    # logging with gunicorn
    if __name__ != "__main__":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # register blueprints
    api_blueprint_v1 = Blueprint("api", __name__, url_prefix="/api/v1")
    api.init_app(api_blueprint_v1)
    api.add_namespace(ns_healthz)
    api.add_namespace(ns_user)
    api.add_namespace(ns_role)
    api.add_namespace(ns_auth)

    app.register_blueprint(api_blueprint_v1)

    # seed database with roles
    @app.cli.command("db_seed")
    def seed_roles_table():
        if models.RolesModel.check_for_roles():
            print("Role table has seeded data. No need to seed!")
        else:
            roles = [
                {"role_name": models.RolesModel(name="Super Admin")},
                {"role_name": models.RolesModel(name="Admin")},
                {"role_name": models.RolesModel(name="General")},
            ]
            for role in roles:
                db.session.add(role.get("role_name"))
            db.session.commit()
            print("Role table has been seeded")

    # seed database with super admin user
    @app.cli.command("db_seed_default_user")
    def seed_with_admin():
        try:
            super_admin = models.UserModel(
                name="Super",
                password=models.UserModel.generate_hash(Config.DEFAULT_USER_PASSWORD),
                role_id=1,
                telephone="",
                is_disabled=False,
                last_login_date=datetime.utcnow(),
                profile_photo="",
                email="superadmin@wallet.co",
            )
            db.session.add(super_admin)
            db.session.commit()
            print("Users table has been seeded successfully with default user")
        except Exception as e:
            print(f"Failure in seeding users table with default user: {str(e)}")

    # check if token is revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(decrypted_token):
        jti = decrypted_token["jti"]
        return models.RevokedTokenModel.is_token_blacklisted(token=jti)

    # CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers="*")
    return app


#
# def main():
#     app = create_app(config["default"])
#     startup_param = {"host": "0.0.0.0", "debug": True}
#     app.run(host='0.0.0.0')


if __name__ == "__main__":
    app = create_app(config["default"])
    app.run(host="0.0.0.0", debug=True)
