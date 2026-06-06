from flask import Flask


def create_app():

    app = Flask(__name__)

    from app.routes.blockchain_routes import (
        blockchain_bp
    )

    app.register_blueprint(
        blockchain_bp
    )

    return app
