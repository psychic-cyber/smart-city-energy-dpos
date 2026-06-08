from flask import Flask


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.secret_key = (
        "smart_city_energy_secret"
    )

    from app.routes.blockchain_routes import (
        blockchain_bp
    )

    from app.routes.dashboard_routes import (
        dashboard_bp
    )

    from app.routes.user_routes import (
        user_bp
    )

    app.register_blueprint(
        blockchain_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        user_bp
    )

    return app