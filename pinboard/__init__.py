from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from pinboard import board
    app.register_blueprint(board.bp)

    return app