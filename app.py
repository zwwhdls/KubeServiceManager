import time
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/ping")
    def ping():
        return jsonify(dict(message="PONG", time=int(time.time())))

    from blueprint import bp

    app.register_blueprint(bp)
    return app


app_object = create_app()
