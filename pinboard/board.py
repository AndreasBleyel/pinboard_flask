from flask import Blueprint, render_template

bp = Blueprint("board", __name__)

@bp.route("/")
def list():
    return render_template("board/list.html")

@bp.route("/add", methods=("GET", "POST"))
def add():
    return render_template("board/add.html")