from flask import Blueprint, render_template, request, redirect, url_for, make_response
from pinboard.db import get_db
import json
from _datetime import datetime

bp = Blueprint("board", __name__)


def evaluate_prio(elem):
    fmt = '%Y-%m-%d %H:%M:%S'
    today = datetime.today()
    created = datetime.strptime(elem["created"], fmt)
    dif = today - created

    #Zeitunterschied zwischen Server und Lokal sind 120 Minuten
    #daher Abzug von 120 von der errechneten Margin
    margin = int(round(dif.total_seconds() / 60)) - 120

    #50 Punkte zum Start jedes Pins
    #jeder Like * 50 - jeder Like zählt 50 Punkte
    #Zeit seit Erstellung in Minuten wird abgezogen
    #Umso höher das Ergebniss, desto höher wird der Pin priorisiert
    prio = 50 + elem["likes"] * 50 - margin

    #print("ID: {}, Margin: {}, Likes: {}, Prio: {}".format(elem["id"], margin, elem["likes"], prio))
    return prio

def get_all_posts(db):
    return db.execute("SELECT * FROM post ORDER BY created DESC").fetchall()

@bp.route("/", methods=("GET", "POST"))
def list():
    db = get_db()

    posts = get_all_posts(db)
    liked_posts_str = {}

    if request.cookies.get("ids"):
        liked_posts_str = json.loads(request.cookies.get("ids"))

    liked_posts_int = []
    for id in liked_posts_str:
        liked_posts_int.append(int(id))

    if request.method == "GET":
        posts.sort(key=evaluate_prio, reverse=True)
        return render_template("board/list.html", posts=posts, liked_posts=liked_posts_int)
    else:
        if request.form["post_id"] in liked_posts_str:
            del liked_posts_str[request.form["post_id"]]
            db.execute("UPDATE post SET likes = likes -1 WHERE id= ? ", request.form["post_id"])
        else:
            liked_posts_str[request.form["post_id"]] = request.form["post_id"]
            db.execute("UPDATE post SET likes = likes +1 WHERE id= ? ", request.form["post_id"])

        liked_posts_int = []
        for id in liked_posts_str:
            liked_posts_int.append(int(id))

        posts = get_all_posts(db)
        db.commit()

        posts.sort(key=evaluate_prio, reverse=True)

        resp = make_response(render_template("board/list.html", posts=posts, liked_posts=liked_posts_int))
        resp.set_cookie("ids", json.dumps(liked_posts_str))
        return resp


@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "GET":
        return render_template("board/add.html")
    else:
        title = request.form["title"]
        desc = request.form["description"]
        color = request.form["color"]

        db = get_db()
        db.execute("INSERT INTO post (title, description, color, likes) VALUES (?,?,?,0)", (title, desc, color))
        db.commit()

        resp = make_response(redirect(url_for("board.list")))

        return resp
